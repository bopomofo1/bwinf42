import math

class BoundingBox():
    def __init__(self, polygon):

        self.left = int(polygon[0][0])
        self.right = int(polygon[0][0])
        self.bottom = int(polygon[0][1])
        self.top = int(polygon[0][1])
        
        # Ausmaße finden
        for point in polygon:
            if point[0] < self.left:
                self.left = int(point[0])
            if point[0] > self.right:
                self.right = int(point[0])
            if point[1] < self.bottom:
                self.bottom = int(point[1])
            if point[1] > self.top:
                self.top = int(point[1])

            self.width = self.right - self.left
            self.height = self.top - self.bottom
        
    def contains_point(self, point):
        if point[0] >= self.left and \
        point[0] <= self.right and \
        point[1] >= self.bottom and \
        point[1] <= self.top:
            return True
        else:
            return False

    def create_smaller_bounding_boxes(self, width, height):
        horizontal = int(math.ceil((self.right - self.left) / width))
        vertical = int(math.ceil((self.top - self.bottom) / height))

        bounding_left_bottom = [self.left, self.bottom]

        smaller_bounding_boxes = []
        for y in range(vertical):
            for x in range(horizontal):
                # Counter-clock-wise
                p1 = [bounding_left_bottom[0] + x * width, bounding_left_bottom[1] + y * height]
                p2 = [p1[0] + width, p1[1]]
                p3 = [p2[0], p2[1] + height]
                p4 = [p3[0] - width, p3[1]]
                
                small_bounding_box = BoundingBox([p1, p2, p3, p4])
                smaller_bounding_boxes.append(small_bounding_box)
                
        return smaller_bounding_boxes