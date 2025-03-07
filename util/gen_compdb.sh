#!/usr/bin/env bash

# Generate a compile_commands.json file.

BUILD_DIR=build

if [ ! -d "$BUILD_DIR" ]; then
    mkdir -p $BUILD_DIR     
fi

cmake -G Ninja -B $BUILD_DIR -S .
ninja -C $BUILD_DIR -t compdb > compile_commands.json