import json
import argparse


class StyleFactory:
    def draw(self, node, prefix="", is_last=True):
        pass


class TreeStyleFactory(StyleFactory):
    def __init__(self, icon_family):
        self.icon_family = icon_family

    def draw(self, node, prefix="", is_last=True):
        lines = []
        connector = "└─ " if is_last else "├─ "
        lines.append(f"{prefix}{connector}{self.icon_family[node.name] + node.name}")
        if node.children:
            new_prefix = prefix + ("   " if is_last else "│  ")
            for i, child in enumerate(node.children):
                lines.extend(self.draw(child, new_prefix, i == len(node.children) - 1))
        return lines


class RectangleStyleFactory(StyleFactory):
    def __init__(self, icon_family):
        self.icon_family = icon_family
        self.flag = 0

    def draw(self, node, prefix="", is_last1=True, is_last2=False):
        lines = []
        box_width = 50
        connector = "├─ "
        # 判断是否为第一行
        if prefix == "" and self.flag == 0:
            lines.append(
                f"{prefix}┌{self.icon_family[node.name] + node.name.ljust(box_width - len(prefix) - len(self.icon_family[node.name]) - 1, '─')}┐")
            self.flag = 1
        elif is_last2 and is_last1:
            prefix = "└──"
            lines.append(
                f"{prefix}┴─{self.icon_family[node.name] + node.name.ljust(box_width - len(prefix) - len(self.icon_family[node.name]) - 2, '─')}┘")
        else:
            lines.append(
                f"{prefix}{connector}{self.icon_family[node.name] + node.name.ljust(box_width - len(prefix) - len(connector) - len(self.icon_family[node.name]), '─')}┤")
        if node.children:
            new_prefix = prefix + "│  "
            for i, child in enumerate(node.children):
                lines.extend(self.draw(child, new_prefix, is_last1, i == len(node.children) - 1))
        return lines

class IconFamilyFactory:
    def __init__(self, config_file):
        self.config_file = config_file
        self.icon_families = self._load_icon_families()

    def _load_icon_families(self):
        with open(self.config_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def create_icon_family(self, family_name):
        return self.icon_families.get(family_name, {})



class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []

    def __str__(self):
        return self.name


class NodeBuilder:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def build(self):
        return Node(self.name, self.children)


class FunnyJsonExplorer:
    def __init__(self, json_file, style_factory):
        self.json_file = json_file
        self.style_factory = style_factory
        self.root = None

    def _load(self):
        with open(self.json_file, 'r') as file:
            data = json.load(file)
            self.root = self._parse(data)

    def _parse(self, data, name="root"):
        # 使用建造者模式创建Node
        builder = NodeBuilder(name)
        if isinstance(data, dict):
            for key, value in data.items():
                child = self._parse(value, key)
                builder.add_child(child)
        return builder.build()

    def show(self):
        if self.root is None:
            print("No data to display")
            return

        # 使用 style_factory 来绘制节点
        for node in self.root.children:
            lines = self.style_factory.draw(node, "", node == self.root.children[-1])
            for line in lines:
                print(line)


def main():
    global icon_factory_class, style_factory_class
    parser = argparse.ArgumentParser(description='Funny JSON Explorer')
    parser.add_argument('-f', '--file', required=True, help='Path to the JSON file')
    parser.add_argument('-s', '--style', required=True, help='Style to use (tree or rectangle)')
    parser.add_argument('-i', '--icon', required=True, help='Icon family to use')

    args = parser.parse_args()

    # 根据参数选择工厂
    icon_factory = IconFamilyFactory("icon.json")
    icon_family = icon_factory.create_icon_family(args.icon)
    # 根据风格参数创建样式工厂
    if args.style == "tree":
        style_factory_class = TreeStyleFactory
    elif args.style == "rectangle":
        style_factory_class = RectangleStyleFactory
    else:
        print("style must be tree or rectangle!")
        exit()
    style_factory = style_factory_class(icon_family)

    explorer = FunnyJsonExplorer(json_file=args.file, style_factory=style_factory)
    explorer._load()
    explorer.show()


if __name__ == '__main__':
    main()
