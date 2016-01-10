from pysh.poc import HierarchicalObject, Shell


def main():
    # TODO add export dict
    globals()['__builtins__'] = HierarchicalObject(globals()['__builtins__'],
                                                   Shell())


if __name__ == "__main__":
    main()
