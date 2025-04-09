bl_info = {
    "name": "Test GN Addon (4.x)",
    "author": "You",
    "version": (1, 0),
    "blender": (4, 4, 0),  # 가정
    "category": "Geometry Nodes",
}

import bpy

def create_gn_tree():
    ng_name = "TestGN_4x"
    if ng_name not in bpy.data.node_groups:
        node_group = bpy.data.node_groups.new(ng_name, 'GeometryNodeTree')
    else:
        node_group = bpy.data.node_groups[ng_name]

    # (1) 이전 노드들/소켓들 정리
    for node in node_group.nodes:
        node_group.nodes.remove(node)
    #node_group.interface.clear_sockets()

    # 기존 소켓을 싹 지우고 싶다면:
    while node_group.interface.inputs:
        node_group.interface.inputs.remove(node_group.interface.inputs[0])
    while node_group.interface.outputs:
        node_group.interface.outputs.remove(node_group.interface.outputs[0])


    # (2) 인터페이스 소켓 정의
    s_curve = node_group.interface.new_socket('NodeSocketGeometry')
    s_curve.name = "Curve"

    s_scale = node_group.interface.new_socket('NodeSocketFloat')
    s_scale.name = "Scale Multiplier"

    s_out = node_group.interface.new_socket('NodeSocketGeometry')
    s_out.name = "Geometry"
    s_out.is_output = True

    # (3) Group Input/Output 노드
    group_input = node_group.nodes.new("NodeGroupInput")
    group_input.location = (-500, 0)
    group_output = node_group.nodes.new("NodeGroupOutput")
    group_output.location = (500, 0)

    # (4) 예시 노드들
    curve_to_points = node_group.nodes.new("GeometryNodeCurveToPoints")
    curve_to_points.location = (-200, 100)

    instance_on_points = node_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points.location = (100, 100)

    realize = node_group.nodes.new("GeometryNodeRealizeInstances")
    realize.location = (300, 100)

    ramp_node = node_group.nodes.new("FunctionNodeColorRamp")
    ramp_node.name = "MyRamp"
    ramp_node.location = (-200, -150)

    param_node = node_group.nodes.new("GeometryNodeInputSplineParameter")
    param_node.location = (-400, -150)

    separate_color = node_group.nodes.new("ShaderNodeSeparateRGB")
    separate_color.location = (0, -150)

    math_mul = node_group.nodes.new("ShaderNodeMath")
    math_mul.operation = 'MULTIPLY'
    math_mul.location = (200, -150)

    # (5) 링크
    links = node_group.links
    # 인풋 소켓(0=Curve, 1=Scale Multiplier)
    links.new(group_input.outputs[0], curve_to_points.inputs["Curve"])
    links.new(param_node.outputs["Factor"], ramp_node.inputs["Fac"])
    links.new(ramp_node.outputs["Color"], separate_color.inputs["Image"])
    links.new(separate_color.outputs["R"], math_mul.inputs[0])
    links.new(group_input.outputs[1], math_mul.inputs[1])

    links.new(curve_to_points.outputs["Points"], instance_on_points.inputs["Points"])
    links.new(instance_on_points.outputs["Instances"], realize.inputs["Geometry"])
    links.new(realize.outputs["Geometry"], group_output.inputs[0])

    # instance_on_points.inputs["Instance"] 는 예시상 비어 둡니다
    # 원한다면 GeometryNodeObjectInfo 노드를 추가 후 연결

    return node_group, ramp_node

class TEST_OT_setup_gn(bpy.types.Operator):
    """액티브 오브젝트(커브)에 GN 모디파이어를 붙이는 예시"""
    bl_idname = "object.test_setup_gn"
    bl_label = "Setup Test GN (4.x)"

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'WARNING'}, "No active object.")
            return {'CANCELLED'}

        if obj.type != 'CURVE':
            self.report({'WARNING'}, "Active object is not a Curve.")
            return {'CANCELLED'}

        node_group, ramp_node = create_gn_tree()

        # 이미 모디파이어가 있는지 확인
        gn_mod = None
        for m in obj.modifiers:
            if m.type == 'NODES' and m.node_group == node_group:
                gn_mod = m
                break
        if not gn_mod:
            gn_mod = obj.modifiers.new("TestGN4x", 'NODES')
            gn_mod.node_group = node_group

        # "Scale Multiplier"를 1.0으로 세팅 (Input_2 등 인덱스가 달라질 수 있음)
        # 실제론 속성명은 "Input_1"일 수도 있으니, 모디파이어 탭에서 확인 후 조정 필요
        # 혹은 아래처럼 .set_input_float(index, value) 등 GeometryNodesModifierHelper API 활용 가능
        gn_mod["Input_2"] = 1.0

        self.report({'INFO'}, "GN Setup Complete")
        return {'FINISHED'}

class TEST_PT_gn_panel(bpy.types.Panel):
    bl_label = "Test GN (4.x)"
    bl_idname = "TEST_PT_gn_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TestGN"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        layout.operator("object.test_setup_gn", text="Setup GN")

        if not obj or obj.type != 'CURVE':
            layout.label(text="(Select a curve object)")
            return

        # GN 모디파이어 찾기
        gn_mod = None
        for m in obj.modifiers:
            if m.type == 'NODES' and m.node_group and m.node_group.name == "TestGN_4x":
                gn_mod = m
                break

        if gn_mod:
            node_group = gn_mod.node_group
            # ColorRamp 노드를 가져와 UI 표시
            ramp_node = node_group.nodes.get("MyRamp")
            if ramp_node:
                layout.label(text="Scale Ramp:")
                layout.template_color_ramp(ramp_node, "color_ramp", expand=True)

            # Scale Multiplier 소켓
            # (모디파이어 Input_x 명이 상황에 따라 달라질 수 있음)
            layout.prop(gn_mod, '["Input_2"]', text="Scale Multiplier")
        else:
            layout.label(text="(No 'TestGN_4x' modifier on this object)")

def register():
    bpy.utils.register_class(TEST_OT_setup_gn)
    bpy.utils.register_class(TEST_PT_gn_panel)

def unregister():
    bpy.utils.unregister_class(TEST_PT_gn_panel)
    bpy.utils.unregister_class(TEST_OT_setup_gn)

if __name__ == "__main__":
    register()
