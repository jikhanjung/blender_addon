bl_info = {
    "name": "GN Interface Example (Blender 4.x)",
    "author": "YourName",
    "version": (1, 0),
    "blender": (4, 4, 0),
    "category": "Geometry Nodes",
}

import bpy

def create_gn_tree_4x():
    ng_name = "MyNodeGroup_4x"
    
    # 노드 그룹이 이미 있으면 삭제하고 새로 만들기
    if ng_name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[ng_name])
    node_group = bpy.data.node_groups.new(ng_name, 'GeometryNodeTree')

    # 1) 기존 인터페이스 항목들(소켓/프로퍼티) 제거 (선택 사항)
    # 'NodeTreeInterface' 객체는 여러 메서드를 지원하지 않음
    # 개별 항목 삭제 대신, 기존 노드 그룹을 삭제하고 새로 만드는 방식으로 변경
    if ng_name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[ng_name])
    node_group = bpy.data.node_groups.new(ng_name, 'GeometryNodeTree')

    # 2) 새 인터페이스 항목 만들기
    #   (1) Geometry 타입 Input 소켓
    curve_in = node_group.interface.new_item(
        type='NodeSocketGeometry',
        name='Curve',
        identifier='Curve',
        description='Input curve geometry',
        direction='INPUT'
    )
    #   (2) Float 프로퍼티 (Scale Multiplier)
    scale_prop = node_group.interface.new_property(
        type='FLOAT',
        name='Scale Multiplier',
        identifier='scale_multiplier',
        description='Scale each instance',
    )
    #   이 프로퍼티를 Input으로 쓸지, Output으로도 쓸지 설정
    scale_prop.is_input = True
    scale_prop.default_value = 1.0
    scale_prop.min_value = 0.0
    scale_prop.max_value = 100.0

    #   (3) Geometry 타입 Output 소켓
    geo_out = node_group.interface.new_item(
        type='NodeSocketGeometry',
        name='Geometry',
        identifier='Geometry',
        description='Output geometry',
        direction='OUTPUT'
    )

    # 3) 노드 모두 삭제 후 새로 구성
    for n in node_group.nodes:
        node_group.nodes.remove(n)

    group_in_node = node_group.nodes.new("NodeGroupInput")
    group_in_node.location = (-400, 0)
    group_out_node = node_group.nodes.new("NodeGroupOutput")
    group_out_node.location = (400, 0)

    # group_in_node의 outputs 는, 우리가 생성한 인터페이스 항목이
    # direction='INPUT' 인 순서대로 매핑됨
    # 예) group_in_node.outputs[0] => Curve
    #     group_in_node.outputs[1] => scale_multiplier (Float 프로퍼티)

    # group_out_node.inputs[0] => Geometry (Output 소켓)

    # 4) 예시 노드: Curve to Points → ...
    curve_to_points = node_group.nodes.new("GeometryNodeCurveToPoints")
    curve_to_points.location = (-100, 100)

    # ColorRamp 노드(4.x)
    ramp_node = node_group.nodes.new("FunctionNodeColorRamp")
    ramp_node.name = "MyColorRamp"
    ramp_node.location = (100, -50)

    # 스플라인 파라미터
    param_node = node_group.nodes.new("GeometryNodeInputSplineParameter")
    param_node.location = (-300, -50)

    # Instance on Points
    instance = node_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance.location = (200, 100)

    # Realize Instances
    realize = node_group.nodes.new("GeometryNodeRealizeInstances")
    realize.location = (400, 100)

    # etc... (SeparateRGB, Math, etc. 필요하면 추가)

    # 5) 링크
    links = node_group.links

    # curve_in (0번) -> Curve to Points
    links.new(group_in_node.outputs[0], curve_to_points.inputs["Curve"])
    links.new(curve_to_points.outputs["Points"], instance.inputs["Points"])
    links.new(instance.outputs["Instances"], realize.inputs["Geometry"])
    links.new(realize.outputs["Geometry"], group_out_node.inputs[0])

    # param -> ramp.fac
    links.new(param_node.outputs["Factor"], ramp_node.inputs["Fac"])

    # scale_multiplier (1번) => 추후 scale 등으로 연결
    # 예시: instance.inputs["Scale"] 에 직접 prop 연결하진 않고, 중간 Math 노드 거칠 수 있음
    # links.new(group_in_node.outputs[1], instance.inputs["Scale"])

    return node_group

class TEST_OT_gn_setup(bpy.types.Operator):
    """오퍼레이터: 현재 선택된 오브젝트에 이 지오메트리 노드를 적용"""
    bl_idname = "object.test_gn_setup_4x"
    bl_label = "Setup GN (4.x)"

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'WARNING'}, "No active object.")
            return {'CANCELLED'}

        node_group = create_gn_tree_4x()

        # 모디파이어 달기
        mod = None
        for m in obj.modifiers:
            if m.type == 'NODES' and m.node_group == node_group:
                mod = m
                break
        if not mod:
            mod = obj.modifiers.new("MyGN4xMod", 'NODES')
            mod.node_group = node_group

        self.report({'INFO'}, "GN setup done.")
        return {'FINISHED'}

class TEST_PT_gn_panel(bpy.types.Panel):
    """N 패널"""
    bl_label = "Test GN 4.x"
    bl_idname = "TEST_PT_gn_4x"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GN4x"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.test_gn_setup_4x", text="Setup GN 4.x")

def register():
    bpy.utils.register_class(TEST_OT_gn_setup)
    bpy.utils.register_class(TEST_PT_gn_panel)

def unregister():
    bpy.utils.unregister_class(TEST_PT_gn_panel)
    bpy.utils.unregister_class(TEST_OT_gn_setup)

if __name__ == "__main__":
    register()