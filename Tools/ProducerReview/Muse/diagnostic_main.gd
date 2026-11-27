extends SceneTree

func _initialize():
	call_deferred("run_review")

func key_d(pressed):
	var event = InputEventKey.new()
	event.physical_keycode = KEY_D
	event.keycode = KEY_D
	event.pressed = pressed
	Input.parse_input_event(event)

func run_review():
	var scene = load("res://Main.tscn").instantiate()
	root.add_child(scene)
	for i in range(5): await physics_frame
	var player = scene.get_node("Player")
	print("PRODUCER_MAIN_TILEMAP_COUNT=" + str(scene.find_children("*", "TileMapLayer", true, false).size()))
	player.call("SetMoveInput", Vector2.ZERO, false)
	var before = player.global_position
	key_d(true)
	for i in range(20): await physics_frame
	var after_injection = player.global_position
	print("PRODUCER_KEYBOARD_AFTER_JOYSTICK_RELEASE_DISTANCE=" + str(before.distance_to(after_injection)))
	player.call("ClearInjectedInput")
	for i in range(20): await physics_frame
	var after_clear = player.global_position
	key_d(false)
	print("PRODUCER_KEYBOARD_CONTROL_DISTANCE=" + str(after_injection.distance_to(after_clear)))
	print("PRODUCER_MAIN_INPUT_LATCH_REPRODUCED=" + str(before.distance_to(after_injection) < 0.1 and after_injection.distance_to(after_clear) > 2.0))
	quit(0)
