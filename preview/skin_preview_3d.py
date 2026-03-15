from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import *
from PIL import Image
import time

ROTATE_SPEED = 100


class SkinPreview(ShowBase):

    def __init__(self, frame, img):
        window_id = frame.winfo_id()

        loadPrcFileData("", "window-type embedded")
        loadPrcFileData("", f"parent-window-handle {window_id}")
        loadPrcFileData("", "win-origin 0 0")

        w = frame.winfo_width()
        h = frame.winfo_height()
        loadPrcFileData("", f"win-size {w} {h}")

        super().__init__()

        self.second_layer = None

        self.img = img
        self.is_slim = True
        self.disableMouse()

        self.camera.setPos(0, -80, 30)
        self.camera.lookAt(0, 0, 20)

        self.last_time = 0

        self.mouse_down = False
        self.last_mouse = None

        self.cam_heading = 0
        self.cam_pitch = 0
        self.cam_distance = 90
        self.target_distance = 90

        self.min_distance = 20
        self.max_distance = 200

        self.dragging = False
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0

        self.heading = 0
        self.pitch = 0

        self.accept("mouse1", self.start_drag)
        self.accept("mouse1-up", self.stop_drag)
        self.accept("wheel_up", self.zoom_in)
        self.accept("wheel_down", self.zoom_out)

        self.setup_light()

        self.base_layer = self.render.attachNewNode("base_layer")
        self.second_layer = self.render.attachNewNode("second_layer")

        self.build_character_base_layer()
        self.build_character_second_layer()

        self.texture = pil_to_texture(self.img)
        self.load_skin()

        self.taskMgr.add(self.update_task, "update")
        self.update_camera()

    # ---------------------

    def setup_light(self):

        ambient = AmbientLight("ambient")
        ambient.setColor((0.7, 0.7, 0.7, 1))

        self.render.setLight(self.render.attachNewNode(ambient))

        sun = DirectionalLight("sun")
        sun.setColor((0.8, 0.8, 0.8, 1))

        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -45, 0)

        self.render.setLight(sun_np)

    # ---------------------

    def build_character_base_layer(self):

        self.head = build_head()
        self.head.reparentTo(self.base_layer)
        self.head.setZ(22)

        self.body = build_body()
        self.body.reparentTo(self.base_layer)
        self.body.setZ(12)

        if self.is_slim:
            self.arm_r = build_right_arm_slim()
            self.arm_r.reparentTo(self.base_layer)
            self.arm_r.setPos(-5.5, 0, 12)

            self.arm_l = build_left_arm_slim()
            self.arm_l.reparentTo(self.base_layer)
            self.arm_l.setPos(5.5, 0, 12)
        else:
            self.arm_r = build_right_arm_slim()
            self.arm_r.reparentTo(self.base_layer)
            self.arm_r.setPos(-6, 0, 12)

            self.arm_l = build_left_arm_slim()
            self.arm_l.reparentTo(self.base_layer)
            self.arm_l.setPos(6, 0, 12)

        self.leg_r = build_right_leg()
        self.leg_r.reparentTo(self.base_layer)
        self.leg_r.setPos(-2, 0, 0)

        self.leg_l = build_left_leg()
        self.leg_l.reparentTo(self.base_layer)
        self.leg_l.setPos(2, 0, 0)

    def build_character_second_layer(self):
        self.head_outer = build_head_outer()
        self.head_outer.reparentTo(self.second_layer)
        self.head_outer.setZ(22)

        self.body_outer = build_body_outer()
        self.body_outer.reparentTo(self.second_layer)
        self.body_outer.setZ(12)

        if self.is_slim:
            self.arm_r_outer = build_right_arm_outer_slim()
            self.arm_r_outer.reparentTo(self.second_layer)
            self.arm_r_outer.setPos(-5.5, 0, 12)

            self.arm_l_outer = build_left_arm_outer_slim()
            self.arm_l_outer.reparentTo(self.second_layer)
            self.arm_l_outer.setPos(5.5, 0, 12)
        else:
            self.arm_r_outer = build_right_arm_outer()
            self.arm_r_outer.reparentTo(self.second_layer)
            self.arm_r_outer.setPos(-6, 0, 12)

            self.arm_l_outer = build_left_arm_outer()
            self.arm_l_outer.reparentTo(self.second_layer)
            self.arm_l_outer.setPos(6, 0, 12)

        self.leg_r_outer = build_right_leg_outer()
        self.leg_r_outer.reparentTo(self.second_layer)
        self.leg_r_outer.setPos(-2, 0, 0)

        self.leg_l_outer = build_left_leg_outer()
        self.leg_l_outer.reparentTo(self.second_layer)
        self.leg_l_outer.setPos(2, 0, 0)

    # ---------------------

    def load_skin(self):

        self.is_slim = is_slim_skin(self.img)

        tex = self.texture
        # tex = pil_to_texture(self.img)

        for part in [
            self.head,
            self.body,
            self.arm_l,
            self.arm_r,
            self.leg_l,
            self.leg_r,
            self.head_outer,
            self.body_outer,
            self.arm_l_outer,
            self.arm_r_outer,
            self.leg_l_outer,
            self.leg_r_outer,
        ]:
            part.setTexture(tex, 1)
            part.setTransparency(True)
            part.setLightOff()

    # ---------------------

    def start_drag(self):

        if self.mouseWatcherNode.hasMouse():

            self.dragging = True

            self.prev_mouse_x = self.mouseWatcherNode.getMouseX()
            self.prev_mouse_y = self.mouseWatcherNode.getMouseY()

    def stop_drag(self):

        self.dragging = False

    # ---------------------

    def zoom_in(self):

        self.target_distance -= 10
        self.target_distance = max(self.min_distance, self.target_distance)

    def zoom_out(self):

        self.target_distance += 10
        self.target_distance = min(self.max_distance, self.target_distance)

    # ---------------------
    def update_camera(self):

        from math import sin, cos, radians

        h = radians(self.cam_heading)
        p = radians(self.cam_pitch)

        x = self.cam_distance * sin(h) * cos(p)
        y = -self.cam_distance * cos(h) * cos(p)
        z = self.cam_distance * sin(p)

        self.camera.setPos(x, y, z + 20)

        self.camera.lookAt(0, 0, 12)

    def update_task(self, task):

        dt = globalClock.getDt()

        if self.dragging and self.mouseWatcherNode.hasMouse():

            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()

            dx = mouse_x - self.prev_mouse_x
            dy = mouse_y - self.prev_mouse_y

            self.cam_heading -= dx * 150
            self.cam_pitch -= dy * 150

            # 上下制限
            self.cam_pitch = max(-85, min(85, self.cam_pitch))

            self.update_camera()

            self.prev_mouse_x = mouse_x
            self.prev_mouse_y = mouse_y

        if time.time() - self.last_time > 1:

            self.load_skin()

            self.last_time = time.time()

        zoom_speed = 10 * globalClock.getDt()
        self.cam_distance += (self.target_distance - self.cam_distance) * zoom_speed
        self.update_camera()

        return task.cont

    def update_texture(self, img):

        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        self.texture.setRamImageAs(img.tobytes(), "RGBA")
        # pixels = model.get_raw_pixels()
        # self.texture.setRamImage(pixels)

    def show_second_layer(self):

        if self.second_layer:
            self.second_layer.show()

    def hide_second_layer(self):

        if self.second_layer:
            self.second_layer.hide()


# --------------------------------
# PIL → Panda3D Texture
# --------------------------------
def pil_to_texture(img):

    img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    tex = Texture()
    tex.setup2dTexture(img.width, img.height, Texture.T_unsigned_byte, Texture.F_rgba)

    tex.setRamImageAs(img.tobytes(), "RGBA")
    tex.setMagfilter(Texture.FT_nearest)
    tex.setMinfilter(Texture.FT_nearest)

    return tex


# --------------------------------
# UV helper
# --------------------------------
def uv(x, y):
    return x / 64.0, 1 - y / 64.0


def uv_rect(x1, y1, x2, y2):

    return [
        uv(x1, y2),
        uv(x2, y2),
        uv(x2, y1),
        uv(x1, y1),
    ]


def uv_rect_top_rot90(x1, y1, x2, y2):

    return [
        uv(x1, y1),
        uv(x1, y2),
        uv(x2, y2),
        uv(x2, y1),
    ]


def uv_rect_bottom_rot90(x1, y1, x2, y2):

    return [
        uv(x2, y2),
        uv(x2, y1),
        uv(x1, y1),
        uv(x1, y2),
    ]


# --------------------------------
# 第一スキンレイヤー
# --------------------------------
def build_head():

    uv_faces = [
        uv_rect_top_rot90(8, 0, 16, 8),  # top
        uv_rect_bottom_rot90(16, 0, 24, 8),  # bottom
        uv_rect(0, 8, 8, 16),  # right
        uv_rect(8, 8, 16, 16),  # front
        uv_rect(16, 8, 24, 16),  # left
        uv_rect(24, 8, 32, 16),  # back
    ]

    return build_cube(8, 8, 8, uv_faces)


def build_body():

    uv_faces = [
        uv_rect_top_rot90(20, 16, 28, 20),
        uv_rect_bottom_rot90(28, 16, 36, 20),
        uv_rect(16, 20, 20, 32),
        uv_rect(20, 20, 28, 32),
        uv_rect(28, 20, 32, 32),
        uv_rect(32, 20, 40, 32),
    ]

    return build_cube(8, 4, 12, uv_faces)


def build_right_arm():

    uv_faces = [
        uv_rect_top_rot90(44, 16, 48, 20),
        uv_rect_bottom_rot90(48, 16, 52, 20),
        uv_rect(40, 20, 44, 32),
        uv_rect(44, 20, 48, 32),
        uv_rect(48, 20, 52, 32),
        uv_rect(52, 20, 56, 32),
    ]

    return build_cube(4, 4, 12, uv_faces)


def build_right_leg():

    uv_faces = [
        uv_rect_top_rot90(4, 20, 8, 20),
        uv_rect_bottom_rot90(8, 16, 12, 20),
        uv_rect(0, 20, 4, 32),
        uv_rect(4, 20, 8, 32),
        uv_rect(8, 20, 12, 32),
        uv_rect(12, 20, 16, 32),
    ]

    return build_cube(4, 4, 12, uv_faces)


def build_left_arm():

    uv_faces = [
        uv_rect_top_rot90(36, 48, 40, 52),
        uv_rect_bottom_rot90(40, 48, 44, 52),
        uv_rect(32, 52, 36, 64),
        uv_rect(36, 52, 40, 64),
        uv_rect(40, 52, 44, 64),
        uv_rect(44, 52, 48, 64),
    ]

    return build_cube(4, 4, 12, uv_faces)


def build_left_leg():

    uv_faces = [
        uv_rect_top_rot90(20, 48, 24, 52),
        uv_rect_bottom_rot90(24, 48, 28, 52),
        uv_rect(16, 52, 20, 64),
        uv_rect(20, 52, 24, 64),
        uv_rect(24, 52, 28, 64),
        uv_rect(28, 52, 32, 64),
    ]

    return build_cube(4, 4, 12, uv_faces)


# --------------------------------
# 第二スキンレイヤー
# --------------------------------
def build_head_outer():

    uv_faces = [
        uv_rect_top_rot90(40, 0, 48, 8),  # top
        uv_rect_bottom_rot90(48, 0, 56, 8),  # bottom
        uv_rect(32, 8, 40, 16),  # right
        uv_rect(40, 8, 48, 16),  # front
        uv_rect(48, 8, 56, 16),  # left
        uv_rect(56, 8, 64, 16),  # back
    ]

    return build_cube(9, 9, 9, uv_faces)


def build_body_outer():

    uv_faces = [
        uv_rect_top_rot90(20, 32, 28, 36),
        uv_rect_bottom_rot90(28, 32, 36, 36),
        uv_rect(16, 36, 20, 48),
        uv_rect(20, 36, 28, 48),
        uv_rect(28, 36, 32, 48),
        uv_rect(32, 36, 40, 48),
    ]

    return build_cube(9, 5, 13, uv_faces)


def build_right_arm_outer():

    uv_faces = [
        uv_rect_top_rot90(44, 32, 48, 36),
        uv_rect_bottom_rot90(48, 32, 52, 36),
        uv_rect(40, 36, 44, 48),
        uv_rect(44, 36, 48, 48),
        uv_rect(48, 36, 52, 48),
        uv_rect(52, 36, 56, 48),
    ]

    return build_cube(5, 5, 13, uv_faces)


def build_right_leg_outer():

    uv_faces = [
        uv_rect_top_rot90(4, 32, 8, 36),
        uv_rect_bottom_rot90(8, 32, 12, 36),
        uv_rect(0, 36, 4, 48),
        uv_rect(4, 36, 8, 48),
        uv_rect(8, 36, 12, 48),
        uv_rect(12, 36, 16, 48),
    ]

    return build_cube(5, 5, 13, uv_faces)


def build_left_arm_outer():

    uv_faces = [
        uv_rect_top_rot90(56, 48, 56, 52),
        uv_rect_bottom_rot90(56, 48, 60, 52),
        uv_rect(48, 52, 52, 64),
        uv_rect(52, 52, 56, 64),
        uv_rect(56, 52, 60, 64),
        uv_rect(60, 52, 64, 64),
    ]

    return build_cube(5, 5, 13, uv_faces)


def build_left_leg_outer():

    uv_faces = [
        uv_rect_top_rot90(4, 48, 8, 52),
        uv_rect_bottom_rot90(8, 48, 12, 52),
        uv_rect(0, 52, 4, 64),
        uv_rect(4, 52, 8, 64),
        uv_rect(8, 52, 12, 64),
        uv_rect(12, 52, 16, 64),
    ]

    return build_cube(5, 5, 13, uv_faces)


# --------------------------------
# 第一スキンレイヤー(SLIM)
# --------------------------------
def build_right_arm_slim():

    uv_faces = [
        uv_rect_top_rot90(44, 16, 47, 20),
        uv_rect_bottom_rot90(47, 16, 50, 20),
        uv_rect(40, 20, 44, 32),
        uv_rect(44, 20, 47, 32),
        uv_rect(47, 20, 51, 32),
        uv_rect(51, 20, 54, 32),
    ]

    return build_cube(3, 4, 12, uv_faces)


def build_left_arm_slim():

    uv_faces = [
        uv_rect_top_rot90(36, 48, 39, 52),
        uv_rect_bottom_rot90(39, 48, 42, 52),
        uv_rect(32, 52, 36, 64),
        uv_rect(36, 52, 39, 64),
        uv_rect(39, 52, 43, 64),
        uv_rect(43, 52, 46, 64),
    ]

    return build_cube(3, 4, 12, uv_faces)


# --------------------------------
# 第二スキンレイヤー(SLIM)
# --------------------------------
def build_right_arm_outer_slim():

    uv_faces = [
        uv_rect_top_rot90(44, 32, 47, 36),
        uv_rect_bottom_rot90(47, 32, 50, 36),
        uv_rect(40, 36, 44, 48),
        uv_rect(44, 36, 47, 48),
        uv_rect(47, 36, 51, 48),
        uv_rect(51, 36, 54, 48),
    ]

    return build_cube(4, 5, 13, uv_faces)


def build_left_arm_outer_slim():

    uv_faces = [
        uv_rect_top_rot90(52, 48, 55, 52),
        uv_rect_bottom_rot90(55, 48, 58, 52),
        uv_rect(48, 52, 52, 64),
        uv_rect(52, 52, 55, 64),
        uv_rect(55, 52, 59, 64),
        uv_rect(59, 52, 62, 64),
    ]

    return build_cube(4, 5, 13, uv_faces)


# --------------------------------
# Cube builder with UV
# --------------------------------
def build_cube(size_x, size_y, size_z, uv_faces):

    format = GeomVertexFormat.getV3t2()
    vdata = GeomVertexData("cube", format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, "vertex")
    texcoord = GeomVertexWriter(vdata, "texcoord")

    tris = GeomTriangles(Geom.UHStatic)

    x = size_x / 2
    y = size_y / 2
    z = size_z / 2

    faces = [
        # TOP (+Z)
        [(-x, y, z), (-x, -y, z), (x, -y, z), (x, y, z)],
        # BOTTOM (-Z)
        [(-x, -y, -z), (-x, y, -z), (x, y, -z), (x, -y, -z)],
        # RIGHT (+X)
        [(-x, y, -z), (-x, -y, -z), (-x, -y, z), (-x, y, z)],
        # FRONT (+Y)
        [(-x, -y, -z), (x, -y, -z), (x, -y, z), (-x, -y, z)],
        # LEFT (-X)
        [(x, -y, -z), (x, y, -z), (x, y, z), (x, -y, z)],
        # BACK (-Y)
        [(x, y, -z), (-x, y, -z), (-x, y, z), (x, y, z)],
    ]

    for i in range(6):

        face = faces[i]
        uv_face = uv_faces[i]

        start = vertex.getWriteRow()

        for j in range(4):

            vertex.addData3(*face[j])
            texcoord.addData2(*uv_face[j])

        tris.addVertices(start, start + 1, start + 2)
        tris.addVertices(start, start + 2, start + 3)

    geom = Geom(vdata)
    geom.addPrimitive(tris)

    node = GeomNode("cube")
    node.addGeom(geom)

    return NodePath(node)


def is_slim_skin(img):

    # Alexスキンはこのピクセルが透明
    r, g, b, a = img.getpixel((54, 20))

    return a == 0
