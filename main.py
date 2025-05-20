import numpy as np
import matplotlib.pyplot as plt

draw = False

def write_to_mif(name: str, data: list):
    with open(name, 'w') as file:
        depth = 2 ** int(np.ceil(np.log2(len(data))))
        file.write("WIDTH=11;\n")
        file.write(f"DEPTH={depth};\n\n")
        file.write("ADDRESS_RADIX=UNS;\n\n")
        file.write("DATA_RADIX=UNS;\n\n")
        file.write("CONTENT BEGIN\n")
        for i, val in enumerate(data):
            file.write(f"\t{i}\t:\t{val};\n")
        file.write(f"\t[{len(data)}..{depth - 1}]\t:\t0;\n")
        file.write("END;")


def rotate_lines(theta, origin, lines):
    translated = []
    for line in lines:
        start = np.subtract(line[0], origin)
        end = np.subtract(line[1], origin)
        translated += ((start, end),)
    
    # rotation_matrix = np.array([[1., 0., 0.],  # z
    #                             [0., np.cos(theta), -np.sin(theta)],
    #                             [0., np.sin(theta), np.cos(theta)]])


    rotation_matrix = np.array([[np.cos(theta), 0., np.sin(theta)],  # y
                                [0., 1., 0.],
                                [-np.sin(theta), 0., np.cos(theta)]])


    rotated = []
    for line in translated:
        start = np.dot(rotation_matrix, line[0])
        end = np.dot(rotation_matrix, line[1])
        rotated += ((start, end),)
    
    translated = []
    for line in rotated:
        start = np.add(line[0], origin)
        end = np.add(line[1], origin)
        translated += ((start, end),)
    
    return translated
    
def project_lines_onto_plane(camera, plane, lines):
    output = []
    for line in lines:
        point_1 = line[0]
        point_2 = line[1]
        vector_1 = np.subtract(point_1, camera)
        vector_2 = np.subtract(point_2, camera)

        denom = np.dot(plane[1], vector_1)
        if np.isclose(denom, 0):
            raise Exception("No intersection in point and screen")
        t = np.dot(plane[1], np.subtract(plane[0], camera)) / denom
        intersection_1 = np.add(camera, np.multiply(t, vector_1))

        denom = np.dot(plane[1], vector_2)
        if np.isclose(denom, 0):
            raise Exception("No intersection in point and screen")
        t = np.dot(plane[1], np.subtract(plane[0], camera)) / denom
        intersection_2 = np.add(camera, np.multiply(t, vector_2))

        output += ((intersection_1, intersection_2),)
    return output

lines = (
         ((0., 3., 0.), (8., 3., 0.)),
         ((8., 3., 0.), (8., 9., 0.)),
         ((8., 9., 0.), (0., 9., 0.)),
         ((0., 9., 0.), (0., 3., 0.)),  # front panel
         ((1., 4., 0.), (7., 4., 0.)),
         ((7., 4., 0.), (7., 8., 0.)),
         ((7., 8., 0.), (1., 8., 0.)),
         ((1., 8., 0.), (1., 4., 0.)),  # screen
         ((3., 3., 3.), (1., 0., 3.)),
         ((3., 3., 3.), (5., 1., 3.)),  # antennae
         ((8., 3., 0.), (8., 3., 3.)),
         ((8., 3., 3.), (8., 9., 3.)),
         ((8., 9., 3.), (8., 9., 0.)),
        #  ((8., 9., 0.), (8., 3., 0.)),
         ((8., 3., 3.), (8., 6., 7.)),
         ((8., 6., 7.), (8., 9., 7.)),
         ((8., 9., 7.), (8., 9., 3.)),  # side, x = 8
         ((0., 3., 0.), (0., 3., 3.)),
         ((0., 3., 3.), (0., 9., 3.)),
         ((0., 9., 3.), (0., 9., 0.)),
         ((0., 3., 3.), (0., 6., 7.)),
         ((0., 6., 7.), (0., 9., 7.)),
         ((0., 9., 7.), (0., 9., 3.)),  # size, x = 0
         ((8., 3., 3.), (0., 3., 3.)),
         ((8., 6., 7.), (0., 6., 7.)),
         ((8., 9., 7.), (0., 9., 7.)),  # back
        )
center = (4, 6, 3)  # center of TV
camera = (2., 3., -10.)

plane_norm = np.subtract(center, camera)
plane_norm /= np.linalg.norm(plane_norm)
plane_point = camera + plane_norm

plane = (plane_point, plane_norm)

x0s = []
y0s = []
x1s = []
y1s = []

for i, theta in enumerate(np.linspace(0, 2 * np.pi, 60)):
    rotated = rotate_lines(theta, center, lines)
    projections = project_lines_onto_plane(camera, plane, rotated)  # just ignore z for points
    final = []
    for line in projections:
        final += (((.9 * (line[0][0] - 1.), line[0][1] - 2.,), (.9 * (line[1][0] - 1.), line[1][1] - 2.,)),)
    final = np.multiply(250., final)
    rounded = []
    for line in final:
        rounded += (((round(line[0][0]), round(line[0][1])), (round(line[1][0]), round(line[1][1],))),)
    final = rounded

    if draw:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for line in final:
            ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]])
        plt.show()


    for line in final:
        x0s += (line[0][0],)
        y0s += (line[0][1],)
        x1s += (line[1][0],)
        y1s += (line[1][1],)



write_to_mif(f"./mifs/x0s.mif", x0s)
write_to_mif(f"./mifs/x1s.mif", x1s)
write_to_mif(f"./mifs/y0s.mif", y0s)
write_to_mif(f"./mifs/y1s.mif", y1s)

# ax = fig.add_subplot(111)
# for line in projections:
#     ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for line in lines:
    ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], zs=[line[0][2], line[1][2]])

plt.show()
