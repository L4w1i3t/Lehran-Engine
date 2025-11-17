cmake_minimum_required(VERSION 3.15)
project(LehranEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set SDL2 paths
set(SDL2_DIR "${CMAKE_CURRENT_SOURCE_DIR}/deps/SDL2")
set(SDL2_TTF_DIR "${CMAKE_CURRENT_SOURCE_DIR}/deps/SDL2_ttf")
set(SDL2_MIXER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../vcpkg/installed/x64-windows")

# Include directories
include_directories(
    ${SDL2_DIR}/include
    ${SDL2_TTF_DIR}/include
    ${SDL2_MIXER_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Link directories
link_directories(
    ${SDL2_DIR}/lib/x64
    ${SDL2_TTF_DIR}/lib/x64
    ${SDL2_MIXER_DIR}/lib
)

# Source files
set(SOURCES
    main.cpp
)

# Create executable
add_executable(LehranEngine ${SOURCES})

# Link SDL2 libraries
target_link_libraries(LehranEngine 
    SDL2
    SDL2main
    SDL2_ttf
    SDL2_mixer
)

# Windows-specific settings
if(WIN32)
    # Hide console window
    set_target_properties(LehranEngine PROPERTIES
        WIN32_EXECUTABLE TRUE
    )
endif()

# Set output directory
set_target_properties(LehranEngine PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_CURRENT_SOURCE_DIR}/../runtime
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_CURRENT_SOURCE_DIR}/../runtime
)

# Install rules
install(TARGETS LehranEngine
    RUNTIME DESTINATION runtime
)

# Install DLLs
if(WIN32)
    install(FILES 
        "${SDL2_DIR}/lib/x64/SDL2.dll"
        "${SDL2_TTF_DIR}/lib/x64/SDL2_ttf.dll"
        "${SDL2_MIXER_DIR}/bin/SDL2_mixer.dll"
        "${SDL2_MIXER_DIR}/bin/vorbis.dll"
        "${SDL2_MIXER_DIR}/bin/vorbisfile.dll"
        "${SDL2_MIXER_DIR}/bin/ogg.dll"
        "${SDL2_MIXER_DIR}/bin/wavpack.dll"
        DESTINATION runtime
    )
endif()
