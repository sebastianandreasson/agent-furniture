"""Upper post cladding and slim front-facing-book display ledges."""

from __future__ import annotations

from querycad.furniture import PartCatalog
from querycad.models.built_in_bookshelf.layout import BuiltInLayout
from querycad.models.built_in_bookshelf.spec import BuiltInBookshelfSpec
from querycad.models.built_in_bookshelf.subassemblies.materials import DARK_OAK

POST_CLADDINGS = {
    "left": "STRUCTURAL-POST-CLADDING-LEFT-001",
    "middle": "STRUCTURAL-POST-CLADDING-MIDDLE-001",
}
POST_DISPLAY_LEDGES = {
    "left": "POST-DISPLAY-LEDGE-LEFT-001",
    "middle": "POST-DISPLAY-LEDGE-MIDDLE-001",
}
POST_DISPLAY_LIPS = {
    "left": "POST-DISPLAY-LIP-LEFT-001",
    "middle": "POST-DISPLAY-LIP-MIDDLE-001",
}


def add_post_displays(
    catalog: PartCatalog,
    spec: BuiltInBookshelfSpec,
    layout: BuiltInLayout,
) -> None:
    """Clad the upper posts and bridge shelf lines with tiny display ledges."""

    for post in layout.posts:
        catalog.define_stock(
            number=POST_CLADDINGS[post.name],
            description=f"Upper oak face cladding over the {post.name} structural post",
            material=spec.finish_material,
            size_mm=(
                post.width,
                spec.post_trim_thickness,
                layout.post_cladding_height,
            ),
            color=DARK_OAK,
        ).place(
            f"structural_post_cladding_{post.name}",
            (
                post.center_x,
                layout.depths.post_cladding_center_y,
                layout.post_cladding_bottom_z,
            ),
        )
        ledges = catalog.define_stock(
            number=POST_DISPLAY_LEDGES[post.name],
            description=f"Slim {post.name}-post display ledge for a front-facing book",
            material=spec.finish_material,
            size_mm=(
                post.width,
                spec.display_ledge_depth,
                spec.display_ledge_thickness,
            ),
            color=DARK_OAK,
        )
        lips = catalog.define_stock(
            number=POST_DISPLAY_LIPS[post.name],
            description=f"Low retaining lip on a {post.name}-post display ledge",
            material=spec.finish_material,
            size_mm=(
                post.width,
                spec.display_lip_thickness,
                spec.display_lip_height,
            ),
            color=DARK_OAK,
        )
        for shelf_index, display_level in enumerate(layout.post_display_levels, start=1):
            ledges.place(
                f"post_display_ledge_{post.name}_{shelf_index:02d}",
                (
                    post.center_x,
                    layout.depths.display_ledge_back_y - spec.display_ledge_depth / 2,
                    display_level - spec.display_ledge_thickness,
                ),
            )
            lips.place(
                f"post_display_lip_{post.name}_{shelf_index:02d}",
                (
                    post.center_x,
                    layout.depths.display_ledge_back_y
                    - spec.display_ledge_depth
                    + spec.display_lip_thickness / 2,
                    display_level,
                ),
            )
