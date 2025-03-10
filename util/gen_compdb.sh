#!/usr/bin/env bash

# Generate a compile_commands.json file.

BUILD_DIR=build

if [ ! -d "$BUILD_DIR" ]; then
    mkdir -p $BUILD_DIR     
fi

cmake -G Ninja -DZ3_TRUST_SYSTEM_VERSION=on -DSYMCC_RT_BACKEND=simple -DLLVM_DIR=/llvm_source/build -B $BUILD_DIR -S .
ninja -C $BUILD_DIR -t compdb > compile_commands.json
ninja -C $BUILD_DIR/SymCCRuntime-prefix/src/SymCCRuntime-build -t compdb >> runtime/compile_commands.json