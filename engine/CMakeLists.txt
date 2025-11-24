cmake_minimum_required(VERSION 3.15)
project(LehranEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set vcpkg toolchain
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/../vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "Vcpkg toolchain file")

# Include our custom headers
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Find SDL2 packages via vcpkg
find_package(SDL2 CONFIG REQUIRED)
find_package(SDL2_ttf CONFIG REQUIRED)
find_package(SDL2_image CONFIG REQUIRED)
# Note: SDL2_mixer doesn't have a CONFIG mode, using MODULE mode
find_package(SDL2_mixer REQUIRED)

# Source files
set(SOURCES
    main.cpp
    src/SaveManager.cpp
    src/TextureManager.cpp
    src/SaveSlotScreen.cpp
    src/SceneManager.cpp
    src/DialogueSystem.cpp
)

# Create executable
add_executable(LehranEngine ${SOURCES})

# Link SDL2 libraries using modern CMake targets
target_link_libraries(LehranEngine 
    PRIVATE
    $<TARGET_NAME_IF_EXISTS:SDL2::SDL2main>
    $<IF:$<TARGET_EXISTS:SDL2::SDL2>,SDL2::SDL2,SDL2::SDL2-static>
    $<IF:$<TARGET_EXISTS:SDL2_ttf::SDL2_ttf>,SDL2_ttf::SDL2_ttf,SDL2_ttf::SDL2_ttf-static>
    $<IF:$<TARGET_EXISTS:SDL2_image::SDL2_image>,SDL2_image::SDL2_image,SDL2_image::SDL2_image-static>
    SDL2_mixer::SDL2_mixer
)

# Windows-specific settings
if(WIN32)
    # Hide console window in release builds only
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        set_target_properties(LehranEngine PROPERTIES
            WIN32_EXECUTABLE TRUE
        )
    endif()
endif()

# Set output directory (directly to runtime, not runtime/Release)
set_target_properties(LehranEngine PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../runtime
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_CURRENT_SOURCE_DIR}/../runtime
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_CURRENT_SOURCE_DIR}/../runtime
)

# Copy DLLs to runtime directory automatically
if(WIN32)
    add_custom_command(TARGET LehranEngine POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:SDL2::SDL2>
            $<TARGET_FILE_DIR:LehranEngine>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:SDL2_ttf::SDL2_ttf>
            $<TARGET_FILE_DIR:LehranEngine>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:SDL2_image::SDL2_image>
            $<TARGET_FILE_DIR:LehranEngine>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_FILE:SDL2_mixer::SDL2_mixer>
            $<TARGET_FILE_DIR:LehranEngine>
        COMMENT "Copying SDL2 DLLs to output directory"
    )
endif()
