#!/usr/bin/env bash
# This script generates stubs for the given Python files using Pyright.

set -euo pipefail

source .venv/bin/activate

function generate_stubs_for_dir(){
    local dir=$1
    local output_dir=$2
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
                echo "Generating stubs for dir: $file"
                generate_stubs_for_dir "$dir/$file" "$output_dir/$file"
            fi
            if [ -f "$dir/$file" ]; then
                if [[ $file != *.py ]]; then
                    echo "Invalid file type: $file"
                    continue
                fi
                echo "Generating stubs for file: $file"
                stubgen -o "$output_dir" "$dir/$file"
            fi
        done
    fi
    echo "=========================="
}
generate_stubs_for_dir "./src/fastapi_factory_utilities" "src/fastapi_factory_utilities"
