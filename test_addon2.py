bl_info = {
    "name": "Add Cube with Panel",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N Panel > My Addon",
    "description": "Adds a cube and has a simple panel",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy

# 1. 'Hello World!'를 출력하는 간단한 오퍼레이터
class OBJECT_OT_hello_world(bpy.types.Operator):
    """이 오퍼레이터는 'Hello World!' 문구를 출력합니다."""
    bl_idname = "object.hello_world"
    bl_label = "Hello World Operator"

    def execute(self, context):
        self.report({'INFO'}, "Hello World!")
        return {'FINISHED'}

# 2. 큐브를 추가하는 오퍼레이터
class OBJECT_OT_add_cube(bpy.types.Operator):
    """이 오퍼레이터는 큐브를 추가합니다."""
    bl_idname = "object.add_cube"
    bl_label = "Add Cube Operator"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        self.report({'INFO'}, "Cube Added!")
        return {'FINISHED'}

# 3. (선택) Object 메뉴에 오퍼레이터를 추가하기 위한 함수
#    만약 N 패널만 사용하고 싶다면 이 부분과 register/unregister에서의 해당 부분을 빼도 됩니다.
def menu_func(self, context):
    layout = self.layout
    layout.operator(OBJECT_OT_hello_world.bl_idname, text="Hello World Operator")
    layout.operator(OBJECT_OT_add_cube.bl_idname, text="Add Cube Operator")

# 4. 'N 패널'에 표시될 패널 클래스
class VIEW3D_PT_my_addon_panel(bpy.types.Panel):
    """사이드바(N 패널)에 표시될 패널"""
    bl_label = "My Addon Panel"
    bl_idname = "VIEW3D_PT_my_addon_panel"
    bl_space_type = 'VIEW_3D'      # 3D 뷰 스페이스에서 사용
    bl_region_type = 'UI'          # UI 영역 (N 패널)
    bl_category = "My Addon"       # N 패널 탭 이름

    def draw(self, context):
        layout = self.layout
        layout.label(text="Hello, I'm a panel!")
        layout.operator("object.add_cube", text="Add Cube")
        layout.operator("object.hello_world", text="Hello World")

# 5. 애드온 활성화 시 호출될 register 함수
def register():
    bpy.utils.register_class(OBJECT_OT_hello_world)
    bpy.utils.register_class(OBJECT_OT_add_cube)
    bpy.utils.register_class(VIEW3D_PT_my_addon_panel)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # (선택) Object 메뉴에 버튼 추가

# 6. 애드온 비활성화 시 호출될 unregister 함수
def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)  # (선택)
    bpy.utils.unregister_class(VIEW3D_PT_my_addon_panel)
    bpy.utils.unregister_class(OBJECT_OT_add_cube)
    bpy.utils.unregister_class(OBJECT_OT_hello_world)

# 7. 스크립트를 직접 실행할 때(예: 블렌더 텍스트 에디터에서 'Run Script')
if __name__ == "__main__":
    register()
