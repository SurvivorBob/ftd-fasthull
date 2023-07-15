#!/usr/bin/env python3
"""
Makes a hull (see README).

License information:

   Copyright 2023 SurvivorBob <ftd-fasthull@survivorbob.xyz>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

import json
import sys
import argparse
import math

def vector_add(a, b):
    return tuple(map(lambda x, y: x + y, a, b))

def vector_inv(a):
    return tuple(map(lambda x: -x, a))

def vector_mul(a, k):
    return tuple(map(lambda x: k * x, a))

single_block_id = 100000
beam_ids = {
    2: 100001,
    3: 100002,
    4: 100003,
}
inverted_ids = {
    1: 100011,
    2: 100012,
    3: 100013,
    4: 100014,
}
corner_ids = {
    1: 100021,
    2: 100022,
    3: 100023,
    4: 100024,
}
slope_ids = {
    1: 100031,
    2: 100032,
    3: 100033,
    4: 100034,
}

def place_block(blueprint, v, bid, rot = 0, color = 0):
    blueprint["Blueprint"]["BLP"].append("{0},{1},{2}".format(v[0], v[1], v[2]))
    blueprint["Blueprint"]["BLR"].append(rot)
    blueprint["Blueprint"]["BCI"].append(color)
    blueprint["Blueprint"]["BlockIds"].append(bid)
    blueprint["Blueprint"]["TotalBlockCount"] += 1
    blueprint["Blueprint"]["AliveCount"] += 1

def main():
    ap = argparse.ArgumentParser(description="Generates a simple boat hull, copying the author tag from a donor blueprint.")
    ap.add_argument("donor_blueprint", type=str, help="The donor blueprint from which to copy the author tag.")
    ap.add_argument("output_blueprint", type=str, help="The output file name for the blueprint to produce.")
    ap.add_argument("width", type=int, help="The width of the main cuboid.")
    ap.add_argument("height", type=int, help="The height of the main cuboid.")
    ap.add_argument("length", type=int, help="The length of the main cuboid.")
    ap.add_argument("slope", type=int, choices=[1,2,3,4], help="Slope of front (1-4)")
    ap.add_argument("side_armor", type=int, help="Number of _additional_ side armor layers.")
    ap.add_argument("deck_armor", type=int, help="Number of _additional_ deck armor layers.")
    ap.add_argument("bottom_armor", type=int, help="Number of _additional_ bottom armor layers.")

    args = ap.parse_args(sys.argv[1:])

    target_width = args.width + 2 + 2 * args.side_armor
    target_height = args.height + 2 + args.deck_armor + args.bottom_armor
    target_length = args.length + 1 + args.side_armor

    with open(args.donor_blueprint, mode="r") as donor_blueprint_file:
        donor_blueprint = json.load(donor_blueprint_file)

    # preprocess the donor blueprint
    del donor_blueprint["Blueprint"]["VehicleData"]
    del donor_blueprint["Blueprint"]["CSI"]
    del donor_blueprint["SavedMaterialCost"]
    donor_blueprint["Blueprint"]["ContainedMaterialCost"] = 0.0
    donor_blueprint["ItemDictionary"]["100000"] = "3cc75979-18ac-46c4-9a5b-25b327d99410" # single alloy block
    donor_blueprint["ItemDictionary"]["100001"] = "8f9dbf41-6c2d-4e7b-855d-b2432c6942a2" # 2 alloy block
    donor_blueprint["ItemDictionary"]["100002"] = "649f2aec-6f59-4157-ac01-0122ce2e6dad" # 3 alloy block
    donor_blueprint["ItemDictionary"]["100003"] = "9411e401-27da-4546-b805-3334f200f055" # 4 alloy block

    donor_blueprint["ItemDictionary"]["100011"] = "95a626e6-f1b8-491a-aa31-8de5a2beb513" # single alloy block
    donor_blueprint["ItemDictionary"]["100012"] = "51b37dbf-2beb-425b-a817-89434838c857" # 2 alloy block
    donor_blueprint["ItemDictionary"]["100013"] = "8c2aaf82-442e-46a7-9ea5-1b7862cacb87" # 3 alloy block
    donor_blueprint["ItemDictionary"]["100014"] = "ba5c8d03-9093-47a9-a8cd-b721ceeee1dd" # 4 alloy block
    donor_blueprint["ItemDictionary"]["100021"] = "a4b0d100-c480-4697-b606-489d80a6d376" # single alloy block
    donor_blueprint["ItemDictionary"]["100022"] = "90c9965a-1dcc-4786-a2d2-6299fed7260f" # 2 alloy block
    donor_blueprint["ItemDictionary"]["100023"] = "b2ca635d-350c-4977-b8d4-2b2dd28cd2d7" # 3 alloy block
    donor_blueprint["ItemDictionary"]["100024"] = "a6cfd078-bc39-4ad8-a47f-49097913a27b" # 4 alloy block
    donor_blueprint["ItemDictionary"]["100031"] = "911fe222-f9b2-4892-9cd6-8b154d55b2aa" # single alloy block
    donor_blueprint["ItemDictionary"]["100032"] = "c6176cb5-0a32-4d68-a749-8ee33b2230c1" # 2 alloy block
    donor_blueprint["ItemDictionary"]["100033"] = "a3ea61a8-018c-4277-afd9-ac0a34faa759" # 3 alloy block
    donor_blueprint["ItemDictionary"]["100034"] = "2a3905ff-2030-421d-a2bf-90fba71c1c5e" # 4 alloy block

    donor_blueprint["Blueprint"]["BLP"] = []
    donor_blueprint["Blueprint"]["BLR"] = []
    donor_blueprint["Blueprint"]["BCI"] = []
    donor_blueprint["Blueprint"]["BlockIds"] = []
    donor_blueprint["Blueprint"]["TotalBlockCount"] = 0
    donor_blueprint["Blueprint"]["AliveCount"] = 0

    # +z == forward (rotation 0)
    # +y == up (rotation 10)
    # +x == right (rotation 1)
    x_min, x_max, y_min, y_max, z_min, z_max = 0, 0, 0, 0, 0, 0
    # transform the voxel coordinates

    donor_blueprint["Blueprint"]["MaxCords"] = "{0},{1},{2}".format(x_max, y_max, z_max)
    donor_blueprint["Blueprint"]["MinCords"] = "{0},{1},{2}".format(x_min, y_min, z_min)

    voxel_depths = {}

    # generate the main cuboid
    for z in range(target_length):
        w = target_width
        w_min = -math.floor(w/2)
        w_max = math.floor(w/2)
        for y in range(0, target_height):
            voxel_depths[(w_min, y, z)] = 1
            voxel_depths[(w_max, y, z)] = 1
            for dx in range(args.side_armor):
                if (w_min + dx + 1, y, z) not in voxel_depths:
                    voxel_depths[(w_min + dx + 1, y, z)] = 2 + dx
                if (w_max - dx - 1, y, z) not in voxel_depths:
                    voxel_depths[(w_max - dx - 1, y, z)] = 2 + dx
        for x in range(w_min, w_max + 1):
            voxel_depths[(x, 0, z)] = 1
            for dy in range(args.bottom_armor):
                if (x, dy + 1, z) not in voxel_depths:
                    voxel_depths[(x, dy + 1, z)] = 2 + dy
            voxel_depths[(x, target_height - 1, z)] = 1
            for dy in range(args.deck_armor):
                if (x, target_height - 2 - dy, z) not in voxel_depths:
                    voxel_depths[(x, target_height - 2 - dy, z)] = 2 + dy

    # generate the bow
    w = target_width
    w_min_limit = -math.floor(w/2)
    w_max_limit = math.floor(w/2)
    w_min = w_min_limit
    w_max = w_max_limit
    z = target_length
    y = 0

    z_stride = args.slope
    inverted_block, triangle_block, slope_block = {
        1: (inverted_ids[1], corner_ids[1], slope_ids[1]),
        2: (inverted_ids[2], corner_ids[2], slope_ids[2]),
        3: (inverted_ids[3], corner_ids[3], slope_ids[3]),
        4: (inverted_ids[4], corner_ids[4], slope_ids[4]),
    }[max(min(z_stride, 4), 1)]

    while w_min <= w_max:
        for dz in range(z_stride + 1):
            for x in range(w_min, w_max + 1):
                voxel_depths[(x, y, z - 1 + dz)] = 1
                for dy in range(args.bottom_armor):
                    if (x, dy + 1, z - 1 + dz) not in voxel_depths:
                        voxel_depths[(x, dy + 1, z - 1 + dz)] = 2 + dy
        z += z_stride
        w_min += 1
        w_max -= 1

    front_cursor = z - z_stride
    w_min -= 1
    w_max += 1
    w_min_start = w_min
    w_max_start = w_max

    while y < target_height - 1:
        w_min, w_max = w_min_start, w_max_start
        z = front_cursor
        place_block(donor_blueprint, (w_min - 1, y, z + z_stride), triangle_block, 12, 0)
        place_block(donor_blueprint, (w_max + 1, y, z + z_stride), triangle_block, 16, 0)
        place_block(donor_blueprint, (w_min, y, z + z_stride), slope_block, 12, 0)
        if w_min != w_max:
            place_block(donor_blueprint, (w_max, y, z + z_stride), slope_block, 12, 0)
        while z >= target_length:
            if w_min - 1 >= w_min_limit:
                place_block(donor_blueprint, (w_min - 1, y, z), inverted_block, 12, 0)
            if w_max + 1 <= w_max_limit:
                place_block(donor_blueprint, (w_max + 1, y, z), inverted_block, 16, 0)
            if w_min - 2 >= w_min_limit:
                place_block(donor_blueprint, (w_min - 2, y, z), triangle_block, 12, 0)
            if w_max + 2 <= w_max_limit:
                place_block(donor_blueprint, (w_max + 2, y, z), triangle_block, 16, 0)
            for dz in range(z_stride + 1):
                voxel_depths[(w_min, y, z - 1 + dz)] = 1
                voxel_depths[(w_max, y, z - 1 + dz)] = 1
                for dx in range(min(args.side_armor, (w_max - w_min) // 2)):
                    if (w_min + dx + 1, y, z - 1 + dz) not in voxel_depths or voxel_depths[(w_min + dx + 1, y, z - 1 + dz)] > 2 + dx:
                        voxel_depths[(w_min + dx + 1, y, z - 1 + dz)] = 2 + dx
                    if (w_max - dx - 1, y, z - 1 + dz) not in voxel_depths or voxel_depths[(w_max - dx - 1, y, z - 1 + dz)] > 2 + dx:
                        voxel_depths[(w_max - dx - 1, y, z - 1 + dz)] = 2 + dx
            w_min = max(w_min - 1, w_min_limit)
            w_max = min(w_max + 1, w_max_limit)
            z -= z_stride
        front_cursor += z_stride
        y += 1

    w_min, w_max = w_min_start, w_max_start
    z = front_cursor
    place_block(donor_blueprint, (w_min - 1, y, z + z_stride), triangle_block, 12, 0)
    place_block(donor_blueprint, (w_max + 1, y, z + z_stride), triangle_block, 16, 0)
    place_block(donor_blueprint, (w_min, y, z + z_stride), slope_block, 12, 0)
    if w_min != w_max:
        place_block(donor_blueprint, (w_max, y, z + z_stride), slope_block, 12, 0)
    while z >= target_length:
        if w_min - 1 >= w_min_limit:
            place_block(donor_blueprint, (w_min - 1, y, z), inverted_block, 12, 0)
        if w_max + 1 <= w_max_limit:
            place_block(donor_blueprint, (w_max + 1, y, z), inverted_block, 16, 0)
        if w_min - 2 >= w_min_limit:
            place_block(donor_blueprint, (w_min - 2, y, z), triangle_block, 12, 0)
        if w_max + 2 <= w_max_limit:
            place_block(donor_blueprint, (w_max + 2, y, z), triangle_block, 16, 0)
        for dz in range(z_stride + 1):
            for x in range(w_min, w_max + 1):
                voxel_depths[(x, y, z - 1 + dz)] = 1
                if x > w_min + 1 and x < w_max - 1:
                    for dy in range(args.deck_armor):
                        if (x, y - 1 - dy, z - 1 + dz) not in voxel_depths:
                            voxel_depths[(x, y - 1 - dy, z - 1 + dz)] = 2 + dy
        w_min = max(w_min - 1, w_min_limit)
        w_max = min(w_max + 1, w_max_limit)
        z -= z_stride

    # generate the stern

    z = 0
    for x in range(w_min_limit, w_max_limit + 1):
        for y in range(0, target_height):
            voxel_depths[(x, y, z)] = 1
            for dz in range(args.side_armor):
                if (x, y, z + 1 + dz) not in voxel_depths:
                    voxel_depths[(x, y, z + 1 + dz)] = 2 + dz

    # filter voxels by depth
    voxels_by_depth = {}
    for d in range(31):
        voxels_by_depth[d + 1] = set()

    for v, d in voxel_depths.items():
        if d in voxels_by_depth:
            voxels_by_depth[d].add(v)

    for d in voxels_by_depth.keys():
        print(f"depth {d}: {len(voxels_by_depth[d])}")

    # consolidate beams in z and y axes
    if True:
        def consolidate_beams(fd_offset, rotation):
            nonlocal donor_blueprint

            def scan_from(v, d):
                nonlocal donor_blueprint, visited_voxels, n_beams
                beam_fd = 0
                beam_bk = 0
                if v not in visited_voxels:
                    # scan forward
                    b = v
                    while beam_fd + 1 < 4:
                        b = vector_add(b, fd_offset)
                        if b not in visited_voxels and b in voxels_by_depth[d]:
                            beam_fd += 1
                        else:
                            break
                    # scan backward
                    b = v
                    while beam_bk + 1 < 4 - beam_fd:
                        b = vector_add(b, vector_inv(fd_offset))
                        if b not in visited_voxels and b in voxels_by_depth[d]:
                            beam_bk += 1
                        else:
                            break

                    # find real origin point of beam
                    beam_origin = vector_add(v, vector_mul(fd_offset, -beam_bk))
                    beam_length = 1 + beam_fd + beam_bk

                    if beam_length > 1:
                        block_id = beam_ids[beam_length]
                        place_block(donor_blueprint, beam_origin, block_id, rotation, d - 1)
                        n_beams += 1
                        for i in range(beam_length):
                            pt = vector_add(beam_origin, vector_mul(fd_offset, i))
                            if pt in visited_voxels:
                                print(f"d {d}: pt {pt} already visited???")
                            visited_voxels.add(pt)

            for d in voxels_by_depth.keys():
                visited_voxels = set()
                n_beams = 0
                for v in voxels_by_depth[d]:
                    scan_from(v, d)
                    # scan from across x-axis mirror (attempt to preserve symmetry)
                    if fd_offset[0] == 0:
                        v_mirror = (-v[0], v[1], v[2])
                        if v_mirror in voxels_by_depth[d]:
                            scan_from(v_mirror, d)
                print(f"d {d}: turned {len(visited_voxels)} voxels into {n_beams} beams")
                voxels_by_depth[d] = voxels_by_depth[d] - visited_voxels
                print(f"d {d}: {len(voxels_by_depth[d])} voxels left")

        # consolidate beams (z axis, rotation 0)
        consolidate_beams((0, 0, 1), 0)

        # consolidate beams (y axis, rotation 10)
        consolidate_beams((0, 1, 0), 10)

    # place remaining singleton blocks
    for d in voxels_by_depth.keys():
        for v in voxels_by_depth[d]:
            place_block(donor_blueprint, v, single_block_id, 0, d - 1)

    # do final fixup here

    donor_blueprint["Blueprint"]["BlockState"] = "=0,{0}".format(donor_blueprint["Blueprint"]["TotalBlockCount"])

    donor_blueprint["SavedTotalBlockCount"] = donor_blueprint["Blueprint"]["TotalBlockCount"]
    # donor_blueprint["SavedMaterialCost"] = voxel_count * 5.0
    print("saving...")
    with open(args.output_blueprint, mode="w") as output_blueprint_file:
        json.dump(donor_blueprint, output_blueprint_file)

    print("all done!")

if __name__ == "__main__":
    main()
