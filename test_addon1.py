bl_info = {
    "name": "Add Cube Addon",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),  # 사용 중인 블렌더 버전을 기입
    "location": "View3D > Object",
    "description": "Adds a simple cube",
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

# 3. 메뉴에 두 오퍼레이터를 추가하기 위한 함수
def menu_func(self, context):
    layout = self.layout
    layout.operator(OBJECT_OT_hello_world.bl_idname, text="Hello World Operator")
    layout.operator(OBJECT_OT_add_cube.bl_idname, text="Add Cube Operator")

# 4. 애드온 활성화(Install & Enable) 시 호출될 register 함수
def register():
    bpy.utils.register_class(OBJECT_OT_hello_world)
    bpy.utils.register_class(OBJECT_OT_add_cube)
    bpy.types.VIEW3D_MT_object.append(menu_func)

# 5. 애드온 비활성화(Disable) 시 호출될 unregister 함수
def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_OT_add_cube)
    bpy.utils.unregister_class(OBJECT_OT_hello_world)

# 6. 스크립트를 직접 실행할 때(블렌더 텍스트 에디터에서 'Run Script')
if __name__ == "__main__":
    register()
