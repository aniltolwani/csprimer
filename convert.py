"""
Convert hex to rgb
"""
import regex as re
def six_digit_hex_to_rgb(h_vals: str) -> str:
    # iterate through the string and find the corresponding values
    def hex_to_dec(h: str) -> str:
        return str(int(h, 16))

    r, g, b = h_vals[1:3], h_vals[3:5], h_vals[5:7]
    r, g, b = hex_to_dec(r), hex_to_dec(g), hex_to_dec(b)
    return f'rgb({r} {g} {b})'

def eight_digit_hex_to_rgb(h_vals: str) -> str:
    # iterate through the string and find the corresponding values
    
    rgb_str = six_digit_hex_to_rgb(h_vals[:-2])
    opacity = round(int(h_vals[-2:], 16) / 255, 5)
    
    return rgb_str[:3] + "a" + rgb_str[3:-1] + f" / {opacity})"

def four_digit_hex_to_rgb(h_vals: str) -> str:
    # iterate through the string and find the corresponding values
    r, g, b, o = h_vals[1:5]
    return eight_digit_hex_to_rgb(f"#{r}{r}{g}{g}{b}{b}{o}{o}")

def three_digit_hex_to_rgb(h_vals: str) -> str:
    r, g, b = h_vals[1:4]
    return six_digit_hex_to_rgb(f"#{r}{r}{g}{g}{b}{b}")


def hex_parser(file_str: str) -> str:
    pattern_func = {
       r'#[0-9a-fA-f]{8}': lambda x: eight_digit_hex_to_rgb(x.group(0)), 
       r'#[0-9a-fA-f]{6}': lambda x: six_digit_hex_to_rgb(x.group(0)),
       r'#[0-9a-fA-f]{4}': lambda x: four_digit_hex_to_rgb(x.group(0)),
       r'#[0-9a-fA-f]{3}': lambda x: three_digit_hex_to_rgb(x.group(0)),
    }
    for pattern, func in pattern_func.items():
        file_str = re.sub(pattern, func, file_str)
    return file_str   

def main():
    print("--NEW RUN--")
    test_cases = (
        ("simple.css", "simple_expected.css"),
        ("advanced.css", "advanced_expected.css"),
    )
    
    assert six_digit_hex_to_rgb('#00ff00') == 'rgb(0 255 0)'

    for in_f, out_f in test_cases:
        with open(in_f) as f:
            in_str = f.readlines()
        in_str = "".join(in_str) 
        with open(out_f) as f:
            out_str = f.readlines()
        out_str = "".join(out_str)       
        ret = hex_parser(in_str)
        assert(ret == out_str)
    print("ok")

if __name__ == "__main__":
    main()