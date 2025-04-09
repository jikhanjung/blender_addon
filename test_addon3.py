bl_info = {
    "name": "Arthropod Body Addon (Example)",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (4, 4, 0),  # 가정상 4.4로 표기
    "location": "View3D > N Panel > Arthropod",
    "description": "Repeat an input object along a curve, scale with ColorRamp",
    "warning": "",
    "doc_url": "",
    "category": "Geometry Nodes",
}

import bpy

########################################
# 1) 지오메트리 노드 트리(노드그룹) 생성 함수
########################################

def create_arthropod_nodegroup():
    """
    - 'GN_ArthropodBody'라는 이름의 지오메트리 노드 그룹을 생성(또는 재활용)하고,
    - 내부에 ColorRamp, Instance on Points, Curve Parameter 등을 연결.
    - 반환값: node_group 객체, 그리고 'ColorRamp' 노드 객체
    """
    ng_name = "GN_ArthropodBody"
    if ng_name not in bpy.data.node_groups:
        node_group = bpy.data.node_groups.new(ng_name, 'GeometryNodeTree')
    else:
        node_group = bpy.data.node_groups[ng_name]

    # 노드 전부 삭제 후 다시 생성 (예시를 단순화하기 위함)
    for n in node_group.nodes:
        node_group.nodes.remove(n)

    # 1. 그룹 입력/출력 노드
    group_input = node_group.nodes.new("NodeGroupInput")
    group_input.location = (-500, 0)
    group_output = node_group.nodes.new("NodeGroupOutput")
    group_output.location = (800, 0)

    # 2. 그룹 입력 소켓 (Curve, Object, Scale Multiplier 등)
    #    curve: 곡선 오브젝트의 geometry
    node_group.inputs.new('NodeSocketGeometry', "Curve")
    #    instance_obj: instancing할 오브젝트 (Object Info 노드로 불러옴) - 이건 소켓 대신 property 로 받을 수도 있음
    #    하지만 여기서는 "오브젝트 info 노드"를 내부에서 직접 만들어 연결할 것이므로,
    #    필요하다면 'NodeSocketObject' 타입이나 'NodeSocketGeometry'로 추가할 수도 있습니다.
    node_group.inputs.new('NodeSocketFloat', "Scale Multiplier")

    # 3. 그룹 출력 소켓 (Geometry)
    node_group.outputs.new('NodeSocketGeometry', "Geometry")

    # 4. 노드 생성 (Curve to Points, Instance on Points, Realize Instances 등)
    curve_to_points = node_group.nodes.new("GeometryNodeCurveToPoints")
    curve_to_points.location = (-200, 100)

    #   - set mode
    #   - "Count" / "Resolution" / "Length" 등은 취향에 맞게
    #     여기서는 "Count"로 예시
    curve_to_points.inputs["Count"].default_value = 20

    instance_on_points = node_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points.location = (200, 100)

    realize_instances = node_group.nodes.new("GeometryNodeRealizeInstances")
    realize_instances.location = (400, 100)

    # 5. ColorRamp 노드
    color_ramp_node = node_group.nodes.new("FunctionNodeColorRamp")
    color_ramp_node.name = "ColorRamp"
    color_ramp_node.location = (0, -100)

    # 6. Curve Parameter 노드 (0~1로 위치 반환)
    curve_param_node = node_group.nodes.new("GeometryNodeInputSplineParameter")
    curve_param_node.location = (-400, -100)

    # 7. 연결
    #   - GroupInput(Curve) -> CurveToPoints -> InstanceOnPoints -> Realize -> GroupOutput
    node_group.links.new(group_input.outputs["Curve"], curve_to_points.inputs["Curve"])
    node_group.links.new(curve_to_points.outputs["Points"], instance_on_points.inputs["Points"])
    node_group.links.new(instance_on_points.outputs["Instances"], realize_instances.inputs["Geometry"])
    node_group.links.new(realize_instances.outputs["Geometry"], group_output.inputs["Geometry"])

    #   - CurveParameter.Factor -> ColorRamp.Fac
    node_group.links.new(curve_param_node.outputs["Factor"], color_ramp_node.inputs["Fac"])

    #   - ColorRamp.Color -> InstanceOnPoints.Scale (하지만 Scale은 (X,Y,Z) 3D 벡터여야 함)
    #     ColorRamp.Color는 4차원 RGBA가 아니라 3차원 RGB로만 취급하면 (R,G,B)값.
    #     여기서는 편의상 R (즉, 세 채널이 같다고 가정하기 위해 ColorRamp를 흑백 그라디언트로 쓰면 됨)
    #     좀더 정확히 하려면 Separate XYZ, 혹은 Separate Color 쓰는 방법도 있음.
    separate_color = node_group.nodes.new("ShaderNodeSeparateRGB")  # ShaderNodeSeparateRGB 가능
    separate_color.location = (0, -300)

    node_group.links.new(color_ramp_node.outputs["Color"], separate_color.inputs["Image"])

    #   - separate_color.R -> multiply -> Scale
    math_multiply = node_group.nodes.new("ShaderNodeMath")
    math_multiply.operation = 'MULTIPLY'
    math_multiply.location = (200, -300)

    # 그룹 인풋(Scale Multiplier)와 color ramp 값을 곱하기
    node_group.links.new(separate_color.outputs["R"], math_multiply.inputs[0])
    node_group.links.new(group_input.outputs["Scale Multiplier"], math_multiply.inputs[1])

    node_group.links.new(math_multiply.outputs["Value"], instance_on_points.inputs["Scale"])

    # 8. Object Info 노드
    object_info_node = node_group.nodes.new("GeometryNodeObjectInfo")
    object_info_node.location = (-200, -200)
    #   - object_info_node의 Geometry -> Instance on Points의 Instance
    node_group.links.new(object_info_node.outputs["Geometry"], instance_on_points.inputs["Instance"])

    return node_group, color_ramp_node

########################################
# 2) 오퍼레이터: 현재 선택한 오브젝트(곡선)에 지오메트리 노드 모디파이어 세팅
########################################

class OBJECT_OT_setup_arthropod_gn(bpy.types.Operator):
    """현재 선택된 오브젝트(Bezier Curve)에 GN_ArthropodBody 모디파이어를 달고,
    ColorRamp 및 Scale 설정을 할 수 있도록 준비합니다."""
    bl_idname = "object.setup_arthropod_gn"
    bl_label = "Setup Arthropod GN"

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'WARNING'}, "No active object.")
            return {'CANCELLED'}

        # 만약 커브(Object Data)가 Curve 타입인지 체크
        if obj.type != 'CURVE':
            self.report({'WARNING'}, "Active object is not a Curve.")
            return {'CANCELLED'}

        # 1. 노드 그룹 생성
        node_group, color_ramp_node = create_arthropod_nodegroup()

        # 2. 이미 모디파이어가 있는지 확인하거나 새로 생성
        gn_modifier = None
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group == node_group:
                gn_modifier = mod
                break
        if not gn_modifier:
            gn_modifier = obj.modifiers.new("ArthropodBody", 'NODES')
            gn_modifier.node_group = node_group

        # 3. 입력 값 설정 (scale multiplier 등)
        #    (이 부분은 모디파이어의 [Input Attributes]로 노출시킬 수도 있고,
        #     또는 패널에서 prop으로 조절하게 할 수도 있습니다.)
        #    우선 기본값만 설정
        gn_modifier["Input_2"] = 1.0  # (Input_2 = Scale Multiplier 소켓)

        # 4. 모든 설정 완료
        self.report({'INFO'}, f"Geometry Nodes modifier applied to {obj.name}.")
        return {'FINISHED'}

########################################
# 3) 패널: N 패널에서 ColorRamp와 기타 속성 노출
########################################

class VIEW3D_PT_arthropod_panel(bpy.types.Panel):
    """N 패널에 ColorRamp UI와 모디파이어 입력 노출"""
    bl_label = "Arthropod Body"
    bl_idname = "VIEW3D_PT_arthropod_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Arthropod"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        layout.operator("object.setup_arthropod_gn", text="Setup Arthropod GN")

        # 현재 액티브 오브젝트가 GN_ArthropodBody 모디파이어를 갖고 있을 경우
        # 그 ColorRamp 노드를 표시
        if not obj or obj.type != 'CURVE':
            layout.label(text="(Select a Curve object)")
            return

        gn_mod = None
        for m in obj.modifiers:
            if m.type == 'NODES' and m.node_group and m.node_group.name == "GN_ArthropodBody":
                gn_mod = m
                break

        if gn_mod:
            node_group = gn_mod.node_group
            # ColorRamp 노드 찾기
            ramp_node = node_group.nodes.get("ColorRamp")
            if ramp_node:
                layout.label(text="Scale Ramp:")
                layout.template_color_ramp(ramp_node, "color_ramp", expand=True)

            # Scale Multiplier 노출 (모디파이어 Input_2 소켓)
            layout.prop(gn_mod, '[\"Input_2\"]', text="Scale Multiplier")
        else:
            layout.label(text="(No ArthropodBody modifier found)")

########################################
# 4) 레지스터
########################################

classes = (
    OBJECT_OT_setup_arthropod_gn,
    VIEW3D_PT_arthropod_panel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
