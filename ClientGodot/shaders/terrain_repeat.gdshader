shader_type canvas_item;
render_mode unshaded;
uniform sampler2D terrain_atlas : filter_nearest, repeat_disable;
uniform vec2 atlas_cell = vec2(0.0);
uniform float world_period = 128.0;
varying vec2 world_pixel;
void vertex() {
    world_pixel = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}
void fragment() {
    // Mirrored repeats share boundary samples, preventing abrupt tile edge color seams.
    vec2 p = floor(world_pixel);
    vec2 repeat_uv = abs(fract(p / (world_period * 2.0)) * 2.0 - 1.0);
    vec2 atlas_uv = (atlas_cell * 512.0 + vec2(0.5) + repeat_uv * 511.0) / vec2(1536.0, 1024.0);
    COLOR = texture(terrain_atlas, atlas_uv);
}
