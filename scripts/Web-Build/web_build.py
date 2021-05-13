# To build hazel for web:
#   - Take in command line args for debug/release
#   - Build libraries
#   - Build Sandbox App

import sys, getopt, os, colorama, http.server, socketserver, re, subprocess, pathlib, datetime, shutil, zipfile

HTTP_PORT = 8000
output_dir = "./output"
lib_dir = "/lib"
lib_int_dir = lib_dir + "/int"
bin_dir = "/bin"

imgui_dir = "../../Hazel/vendor/imgui/"
glad_dir = "../../Hazel/vendor/Glad/"
glfw_dir = "../../Hazel/vendor/GLFW/"
yaml_cpp_dir = "../../Hazel/vendor/yaml-cpp/"
glm_dir = "../../Hazel/vendor/glm/"
stb_image_dir = "../../Hazel/vendor/stb_image/"
entt_dir = "../../Hazel/vendor/entt/"
imguizmo_dir = "../../Hazel/vendor/ImGuizmo/"

hazel_dir = "../../Hazel/"

#global_flags = ["-g", "-O3"]
debug_flags = ["-g"]
release_flags = ["-O3"]
shell_file = "template/hazel_template.html"

libs = {
        "imgui": {
                "files": [
                        imgui_dir + "imconfig.h",
                        imgui_dir + "imgui.h",
                        imgui_dir + "imgui.cpp",
                        imgui_dir + "imgui_draw.cpp",
                        imgui_dir + "imgui_internal.h",
                        imgui_dir + "imgui_widgets.cpp",
                        imgui_dir + "imstb_rectpack.h",
                        imgui_dir + "imstb_textedit.h",
                        imgui_dir + "imstb_truetype.h",
                        imgui_dir + "imgui_demo.cpp"
                    ],
                "defines": [],
                "flags": [
                        "-s USE_WEBGL2=1",
                        "-s FULL_ES3=1",
                        "-s USE_GLFW=3"
                    ]
            },
##        "Glad": {
##                "files": [
##                        glad_dir + "include/glad/glad.h",
##                        glad_dir + "include/KHR/khrplatform.h",
##                        glad_dir + "src/glad.c"
##                    ],
##                "defines": [],
##                "flags": []
##            },
##        "GLFW": {
##                "files": [
##                        glfw_dir + "include/GLFW/glfw3.h",
##                        glfw_dir + "include/GLFW/glfw3native.h",
##                        glfw_dir + "src/glfw_config.h",
##                        glfw_dir + "src/context.c",
##                        glfw_dir + "src/init.c",
##                        glfw_dir + "src/input.c",
##                        glfw_dir + "src/monitor.c",
##                        glfw_dir + "src/vulkan.c",
##                        glfw_dir + "src/window.c"
##                    ],
##                "defines": [],
##                "flags": []
##            },
        "yaml-cpp": {
                "files": [
                        yaml_cpp_dir + "src/**.h",
                        yaml_cpp_dir + "src/**.cpp",
                        yaml_cpp_dir + "include/**.h"
                    ],
                "defines": [
                    ],
                "flags": [
                        "-I" + yaml_cpp_dir + "include"
                    ]
            },
        "Hazel": {
                "files": [
                        hazel_dir + "src/**.h",
                        hazel_dir + "src/**.cpp",
                        hazel_dir + "vendor/stb_image/**.h",
                        hazel_dir + "vendor/stb_image/**.cpp",
                        hazel_dir + "vendor/glm/glm/**.hpp",
                        hazel_dir + "vendor/glm/glm/**.inl",
                        hazel_dir + "vendor/ImGuizmo/ImGuizmo.h",
                        hazel_dir + "vendor/ImGuizmo/ImGuizmo.cpp"
                    ],
                "defines": [
                        "_CRT_SECURE_NO_WARNINGS",
                        "GLFW_INCLUDE_NONE"
                    ],
                "flags": [
                        "-I" + hazel_dir + "src",
                        "-I" + hazel_dir + "vendor/spdlog/include",
                        #"-I" + glfw_dir + "include",
                        "-I" + imgui_dir,
                        "-I" + glm_dir,
                        "-I" + stb_image_dir,
                        "-I" + entt_dir + "include",
                        "-I" + yaml_cpp_dir + "include",
                        "-I" + imguizmo_dir,
                        "-std=c++17",
                        "-s USE_WEBGL2=1",
                        "-s FULL_ES3=1",
                        "-s USE_GLFW=3"
                    ]
            }
    }

app_dir = "../../Sandbox/"
app_files = [
        app_dir + "src/**.h",
        app_dir + "src/**.cpp"
    ]
app_defines = []
app_flags = [
        "-I" + hazel_dir + "src",
        "-I" + hazel_dir + "vendor",
        "-I" + glm_dir,
        "-I" + entt_dir + "include",
        "-I" + hazel_dir + "vendor/spdlog/include",
        "-std=c++17",
        "-s USE_WEBGL2=1",
        "-s FULL_ES3=1",
        "-s USE_GLFW=3",
        "--preload-file ../../Sandbox/assets@assets"
    ]
app_ld_flags = [
        "--preload-file ../../Sandbox/assets@assets"
    ]

def usage():
    print("Usage:")
    print(" - python web_build.py --task=<task>")
    print(" - python web_build.py --help")
    print("")
    print("(requires python3)")
    print("task:")
    print(" - build")
    print(" - run")
    print(" - all")
    print(" - clean")
	
def task_build(global_flags):
    print("Building the project...")
    if "EMSDK" not in os.environ:
        print("Make sure you have emsdk set up correctly")
        sys.exit()
    if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
    if not os.path.isdir(output_dir + lib_dir):
            os.mkdir(output_dir + lib_dir)
    if not os.path.isdir(output_dir + lib_int_dir):
            os.mkdir(output_dir + lib_int_dir)
    if not os.path.isdir(output_dir + bin_dir):
            os.mkdir(output_dir + bin_dir)
    # compile libraries
    libraries = []
    recompile_exe = True
    for lib in libs:
        print("Building library: ", lib)
        compile_result = compile_lib(lib, libs[lib]["files"], libs[lib]["defines"], global_flags + libs[lib]["flags"])
        if compile_result[0]:
            recompile_exe = True
        libraries.append(compile_result[1])

    # compile executable
    print("Compiling executable")
    compile_exe("index", recompile_exe, app_files, app_defines, global_flags + app_flags, libraries)
    print('\a')
    return

def compile_exe(name, force_compile, files, defines, flags, libraries):
    print("Compiling binary: ", name)
    exe_name = output_dir + bin_dir + '/' + name + '.html'
    # command: emcc hello.c -s WASM=1 -o hello.html
    # make one long string of defines and flags
    define_list = " ".join(("-D"+x for x in defines))
    flag_list = " ".join(flags)
    #embedded_files = " ".join(embedded_files)
    
    # grab files with wildcards    
    file_list = []
    for file in files:
        file_list += match_file_wildcards(file)
    file_list = list(dict.fromkeys(file_list)) # remove duplicates

    # compile object files
    if not os.path.isdir(output_dir + bin_dir + '/int'):
        os.mkdir(output_dir + bin_dir + '/int')
        
    int_dir = output_dir + bin_dir + '/int/' + name + '/'
    if not os.path.isdir(int_dir):
        os.mkdir(int_dir)

    objs = build_objs(file_list, int_dir, define_list, flag_list)

    # compile final executable
    if objs[0] or not os.path.isfile(exe_name) or force_compile:
        objs = " ".join(objs[1])
        cmd = "emcc -s WASM=1 --shell-file " + shell_file + " " + flag_list + " -o " + exe_name + " " + objs + ' ' + " ".join(libraries)
        status = os.system(cmd)
        if status != 0:
            sys.exit()
    else:
        print("Skipping executable (already built)")
    
    return

# Compiles a library with a given output file name,
# list of files (can contain wildcards), list of
# defines and list of extra flags.
def compile_lib(library_name, files, defines, flags):
    lib_changed = False
    archive_name = output_dir + lib_dir + "/lib" + library_name + ".a"
    
    # run command emcc <files> -o output_file <flags>
    # make one long string of defines and flags
    define_list = " ".join(("-D"+x for x in defines))
    flag_list = " ".join(flags)

    # grab files with wildcards    
    file_list = []
    for file in files:
        file_list += match_file_wildcards(file)
    file_list = list(dict.fromkeys(file_list)) # remove duplicates
    #file_a = " ".join(file_list)
    #print(file_a)

    # Compile objects and add them to the list
    int_dir = output_dir + lib_int_dir + '/' + library_name + '/'
    if not os.path.isdir(int_dir):
        os.mkdir(int_dir)
    
    objs = build_objs(file_list, int_dir, define_list, flag_list)

    # compile the archive
    if objs[0] or not os.path.isfile(archive_name):
        lib_changed = True
        objs = " ".join(objs[1])
        status = os.system("emar rcs " + archive_name + " " + objs)
        if status != 0:
            sys.exit()
    else:
        print("Skipping library (already built)")
    
    return (lib_changed, archive_name)

# builds one object file
def build_obj(input_file, output_file, flags):
    status = os.system("emcc " + flags + " " + input_file + " -c -o " + output_file)
    if status != 0:
        sys.exit()

# build a list of input files
# returns a tuple of whether the object files were changed and all the object files
def build_objs(files, target_dir, define_list, flag_list):
    file_changed = False

    objs = []
    
    for file in files:
        if ".h" in file or ".inl" in file:
            continue
        #print(file)
        base_start = file.rfind('/')
        base_end = file.rfind('.')
        
        base_name = file[base_start+1:base_end]
        
        out_name = target_dir + base_name + '.o'
        objs.append(out_name)

        # check if the source file has a newer date than the target
        if last_modified(out_name) < last_modified(file):
            print("Compiling: ", file[base_start+1:])
            build_obj(file, out_name, define_list + ' ' + flag_list)
            file_changed = True
    return (file_changed, objs)

# get the last modified time stamp of a file return 0 if the file does not exist
def last_modified(file_path):
    filename = pathlib.Path(file_path)
    if filename.exists():
        return filename.stat().st_mtime
    else:
        return 0

# returns a list of all the files that a given wildcard works with.
# Rules:
# * matches any file in the same directory
# ** mathces ANY file in the same directory and subdirectory
def match_file_wildcards(wildcard):
    file_address = wildcard.rpartition("/")
    #print(file_address[0], ":", file_address[2])
    directory = file_address[0]
    file_wildcard = file_address[2]
    if os.path.isdir(directory):
        return check_directory(directory, file_wildcard)

# recursive function which checks a given directory for files matching the wildcard
def check_directory(directory, wildcard):
    file_list = os.listdir(directory)
    files = []
    regex_wildcard = wildcard.replace('.', '\\.')
    regex_wildcard = regex_wildcard.replace('**', './')
    regex_wildcard = regex_wildcard.replace('*', '.*')
    regex_wildcard = regex_wildcard.replace('/', '*')
    #print(regex_wildcard)
    checker = re.compile(regex_wildcard)
    for file in file_list:
        #print("Checking file: ", file)
        if os.path.isdir(directory + '/' + file) and "**" in wildcard:
            #print("Recursing dir: " + directory + '/' + file)
            files += check_directory(directory + '/' + file, wildcard)
        else:
            # check if the file works with the wildcard
            if checker.match(file):
                files.append(directory + '/' + file)
    return files
    
def task_run():
    print("Running the project...")
    if os.path.isdir(output_dir):
        # run python server
        print("Booting up the python server...")
        run_server(output_dir)
    else:
        print(colorama.Fore.RED + "ERROR: You need to build first!" + colorama.Style.RESET_ALL)
        sys.exit()
    return

def run_server(root_dir):
    os.chdir(root_dir)
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", HTTP_PORT), handler) as httpd:
        print("Server starting on port: ", HTTP_PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutdown requested!")

def task_clean():
    print('Cleaning directory...')
    shutil.rmtree(output_dir)

def zip_files(output, files):
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            zipf.write(file)
    return

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
		
    argv = sys.argv[1:]
	
    task = ''
	
    try:
        opts, args = getopt.getopt(argv, "", ["help", "task="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "--help":
            usage()
            sys.exit()
        elif opt == "--task":
            task = arg
            if task not in ("build", "run", "all", "clean"):
                usage()
                sys.exit()
        else:
            usage()
            sys.exit()
	
    print("Executing task: ", task)
    if(task == "build"):
        task_build(debug_flags)
    elif(task == "run"):
        task_run()
    elif(task == "all"):
        task_clean()
        task_build(release_flags)
        task_run()
    elif(task == "clean"):
        task_clean()
    else:
        usage()
        sys.exit()
