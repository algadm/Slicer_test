cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(Replacor)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/Replacor")
set(EXTENSION_CATEGORY "Tutorials")
set(EXTENSION_CONTRIBUTORS "Alban (UMICH)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/Replacor.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/Replacor/Screenshots/1.png")
set(EXTENSION_DEPENDS
    SlicerDentalModelSeg
    SlicerConda)

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(replaceAll)
add_subdirectory(replaceAllCLI)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
