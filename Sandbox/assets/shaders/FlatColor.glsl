// Flat Color Shader

#type vertex
#ifdef GL_ES
#version 310 es
#else
#version 330 core
#endif

layout(location = 0) in vec3 a_Position;

uniform mat4 u_ViewProjection;
uniform mat4 u_Transform;

void main()
{
	gl_Position = u_ViewProjection * u_Transform * vec4(a_Position, 1.0);
}

#type fragment
#ifdef GL_ES
#version 310 es
#else
#version 330 core
#endif

layout(location = 0) out vec4 color;

uniform vec4 u_Color;

void main()
{
	color = u_Color;
}