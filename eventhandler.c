//acc to windows dows, we create a handle, if we try to access any i/o device in windows and we can createfilea api for that.

#include <windows.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#define BUFFER_SIZE 4096
typedef struct file_notify_buffer{
    DWORD NextEntryOffset;
    DWORD Action;
    DWORD FileNameLength;
    WCHAR FileName[1];
}buffer;

buffer* file_notify_information;

VOID CALLBACK CompletionRoutine(
    DWORD dwErrorCode,
    DWORD dwNumberOfBytesTransferred,
    LPOVERLAPPED lpOverLapped
){
    if (dwErrorCode == ERROR_SUCCESS){
        printf("Change detected. Number of bytes transferred: %lu", dwNumberOfBytesTransferred);
        buffer* notify = (buffer*)file_notify_information;
        while(notify){
            char fileName[MAX_PATH];
            wcstombs(fileName, notify->FileName, notify->FileNameLength / sizeof(WCHAR));
            fileName[notify->FileNameLength / sizeof(WCHAR)] = '\0';
            printf("[CHANGE] File: %s, Action: %lu", fileName, notify->Action);
            DWORD action = notify->Action;
            char oldname[MAX_PATH];
            char newname[MAX_PATH];
            switch (action){
                case FILE_ACTION_ADDED:
                    printf("\nFile %s was added to the directory.", fileName);
                    break;
                case FILE_ACTION_REMOVED:
                    printf("\nFile %s was removed from the directory.", fileName);
                    break;
                case FILE_ACTION_MODIFIED:
                    printf("\nFile %s was modified", fileName);
                    break;
                case FILE_ACTION_RENAMED_OLD_NAME:
                    wcstombs(oldname, notify->FileName, notify->FileNameLength/sizeof(WCHAR));
                    oldname[notify->FileNameLength/sizeof(WCHAR)] = '\0';
                    break;
                case FILE_ACTION_RENAMED_NEW_NAME:
                    printf("\nFile %s has been renamed to %s", oldname, fileName);
                    break;
            }
            if (notify->NextEntryOffset == 0){
                break;
            }
            notify = (buffer*)((BYTE*)notify + notify->NextEntryOffset);
        }
    }
    else{
        printf("\nCompletion/Input Output operation encountered an error: %lu", GetLastError());
    }
}

int main(){
    HANDLE ha;
    ha = CreateFile(
        "D:\\our_cloud\\uploads",
        FILE_LIST_DIRECTORY,
        FILE_SHARE_DELETE | FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED,
        NULL
    );

    if (ha ==  INVALID_HANDLE_VALUE){
        printf("Failed to create directory handle. Error code: %lu", GetLastError());
    }
    else{
        printf("Successfully created directory handle.");
        DWORD dwNotifyFilter = FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_DIR_NAME;
        file_notify_information = (buffer*)malloc(BUFFER_SIZE);
        OVERLAPPED overlapped = {0};
        overlapped.hEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
        while(1){
            ResetEvent(overlapped.hEvent);
            BOOL result = ReadDirectoryChangesW(
                ha,
                file_notify_information,
                sizeof(buffer) + (MAX_PATH * sizeof(WCHAR)),
                TRUE,
                dwNotifyFilter,
                NULL,
                &overlapped,
                NULL
            );
            if (!result) {
                printf("[ERROR] ReadDirectoryChangesW failed! Error: %lu\n", GetLastError());
                break;
            }
            else{
                WaitForSingleObject(overlapped.hEvent, INFINITE);
                DWORD bytesTransferred;
                if (GetOverlappedResult(ha, &overlapped, &bytesTransferred, TRUE)) {
                    CompletionRoutine(ERROR_SUCCESS, bytesTransferred, &overlapped);
                }
            }
        }
    }
    free(file_notify_information);
    CloseHandle(ha);
    return 0;
}