#include "hzpch.h"

#ifndef HZ_PLATFORM_WEB
#define IMGUI_IMPL_OPENGL_LOADER_GLAD
#else
#define IMGUI_IMPL_OPENGL_ES3
#endif
#include <examples/imgui_impl_opengl3.cpp>
#include <examples/imgui_impl_glfw.cpp>
