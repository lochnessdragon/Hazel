#pragma once
#include "Hazel/Core/Base.h"

#ifdef HZ_PLATFORM_WINDOWS

extern Hazel::Application* Hazel::CreateApplication();

void run() {}

int main(int argc, char** argv)
{
	Hazel::Log::Init();

	HZ_PROFILE_BEGIN_SESSION("Startup", "HazelProfile-Startup.json");
	auto app = Hazel::CreateApplication();
	HZ_PROFILE_END_SESSION();

	HZ_PROFILE_BEGIN_SESSION("Runtime", "HazelProfile-Runtime.json");
	app->Run();
	HZ_PROFILE_END_SESSION();

	HZ_PROFILE_BEGIN_SESSION("Shutdown", "HazelProfile-Shutdown.json");
	delete app;
	HZ_PROFILE_END_SESSION();
}

#elif defined(HZ_PLATFORM_WEB)

extern Hazel::Application* Hazel::CreateApplication();

Hazel::Application* app;

void run()
{
	app->Run();
}

int main(int argc, char** argv)
{
	Hazel::Log::Init();
	emscripten_set_main_loop(run, 0, false);
	HZ_CORE_INFO("Application is starting!");
	app = Hazel::CreateApplication();
}

#endif
