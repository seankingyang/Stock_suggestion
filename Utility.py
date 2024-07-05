import plistlib
import prettytable as pt
import re

def MakeTable(input_df, column_index_name=""):
    tb = pt.PrettyTable()
    if column_index_name != "":
        tb.add_column(column_index_name, input_df.index)
    for col in input_df.columns.values:  # df.columns.values: get the name of list(each columns)
        tb.add_column(col, input_df[col])
    return tb


def Load_Plist(path):
    try:
        with open(path, "rb") as file:
            return plistlib.load(file)
    except:
        return None


def Write_Plist(path, root_dict):
    try:
        with open(path, 'wb') as file:
            return plistlib.dump(root_dict, file)
    except:
        return None


def Split_str(input_str, pattern, num=-1):
    return input_str.split(pattern, num)


def List_2_Tuple(input_list):
    if isinstance(input_list, list):
        return tuple(input_list)


def series2list(input_series):
    list = []
    for i in range( len( input_series ) ):
        list.append( input_series[i] )
    return list

# input: ["1","2","3"] ("1","2","3") "1" => [1,2,3], (1,2,3), 1
# format can be "Int","Float", it will make all input be that type, or it will "Auto"
def numerify(input, format="Auto"):
    if isinstance(input, str) or isinstance(input, int) or isinstance(input, float):
        input_type = is_intORfloat(input)
        if input_type != "":
            if format == "Int":
                output = intify(input)
            elif format == "Float":
                output = floatify(input)
            elif format == "Auto":
                if input_type == "Int":
                    output = intify(input)
                elif input_type == "Float":
                    output = floatify(input)
        else:
            output = input
    elif isinstance(input, list) or isinstance(input, tuple):
        output = []
        for i in input:
            i_type = is_intORfloat(i)
            if i_type != "":
                if format == "Int":
                    output.append(intify(i))
                elif format == "Float":
                    output.append(floatify(i))
                elif format == "Auto":
                    if i_type == "Int":
                        output.append(intify(i))
                    elif i_type == "Float":
                        output.append(floatify(i))
            else:
                output.append(i)
        if isinstance(input, tuple):
            output = List_2_Tuple(output)
    else:
        output = input

    return output


def intify(input):
    if is_int(input):
        return int(input)


def floatify(input):
    if is_float(input):
        return float(input)


def isWithStr(input_str, pattern):
    if isinstance(input_str, str):
        if pattern in input_str:
            return True
        else:
            return False
    else:
        return False


def is_float(input_str):
    try:
        float(input_str)
        return True
    except:
        return False


def is_int(input_str):
    try:
        int(input_str)
        return True
    except:
        return False


def is_intORfloat(input_str):
    if is_float(input_str) & is_int(input_str):
        if int(input_str) == float(input_str):
            return "Int"
        else:
            return "Float"
    else:
        return ""


def p_log(print_str_list,log_path,end_s ="\n"):
    file_str = ""
    for i in range(len(print_str_list)):
        if i == 0:
            file_str = print_str_list[i]
        else:
            file_str = file_str + " " + str(print_str_list[i])
    print(file_str, end=end_s)
    file_str = re.sub("\033\[\d*m", "", file_str)
    with open(log_path, 'a+') as f:
        f.write(file_str)
        if end_s == "\n":
            f.write("\r\n")
        else:
            f.write(end_s)
        f.close()



#####Color
class bcolors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m' ## End color
    BOLD = '\033[1m' ## B
    UNDERLINE = '\033[4m' ### _