#!/usr/bin/env bash

set -euo pipefail

# This scripts will delete recursivelly all the stub (.pyi) files in the src directory
function delete_stubs_for_dir(){
    local dir=$1
    echo "=========================="
    echo "$dir"
    if [ ! -d "$dir" ]; then
        echo "Directory $dir does not exist."
    else
        local file_list=$(ls "$dir")
        echo "Files: $file_list"

        for file in $file_list; do
            echo "Processing $dir/$file"
            if [ $file == "__pycache__" ]; then
                echo "Invalid directory name: $file"
                continue
            fi
            if [ -d "$dir/$file" ]; then
                echo "Deleting stubs for dir: $file"
                delete_stubs_for_dir "$dir/$file"
            fi
            if [ -f "$dir/$file" ]; then
                if [[ $file != *.pyi ]]; then
                    echo "Invalid file type: $file"
                    continue
                fi
                echo "Deleting stubs for file: $file"
                rm "$dir/$file"
            fi
        done
    fi
    echo "=========================="
}
delete_stubs_for_dir "./src/fastapi_factory_utilities"
