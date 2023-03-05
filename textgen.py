# text loading
osr_file = open("object_size_ref.txt", 'r')
osr = {}
for line in osr_file.readlines():
    line = line.strip()
    if not line or line[0] == "#":
        continue
    line_data = line.split('=')
    vals = line_data[1].split('x')
    osr[line_data[0]] = float(vals[0])*float(vals[1])

box_prcentage = 0.65  # size of ref reduce to box_percentage so as x y w h
fb_percentage = 0.5  # + or - to normsize


def getText(objs):
    # objs=[{'cls': 'truck', 'x': 7, 'y': 106, 'w': 125, 'h': 87}, {'cls': 'horse', 'x': 215, 'y': 80, 'w': 208, 'h': 267}, {'cls': 'person', 'x': 272, 'y': 20, 'w': 77, 'h': 202}, {'cls': 'person', 'x': 430, 'y': 123, 'w': 19, 'h': 56}, {'cls': 'dog', 'x': 141, 'y': 202, 'w': 54, 'h': 138}, {'cls': 'person', 'x': 477, 'y': 130, 'w': 7, 'h': 10}, {'cls': 'person', 'x': 403, 'y': 131, 'w': 7, 'h': 15}, {'cls': 'person', 'x': 415, 'y': 135, 'w': 7, 'h': 13}, {'cls': 'person', 'x': 424, 'y': 134, 'w': 6, 'h': 13}]
    if len(objs) == 0:
        return "Sorry, nothing can be detected in this image"

    # size: area
    for x in objs:
        x['size'] = x['w']*x['h']
    for x in objs:
        x['mid'] = (x['x']+int(x['w']*0.5), x['y']+int(x['h']*0.5))
    objs.sort(key=lambda x: x['size'], reverse=True)

    # norm size sf=scalefactor
    try:
        sf = osr[objs[0]['cls']]/objs[0]['size']
        for x in objs:
            x['normsize'] = x['size']*sf
    except KeyError:
        pass

    # shrinked_region [x,y,w,h]
    shrinked_region = [objs[0]['x']+objs[0]['w']*((1-box_prcentage)/2), objs[0]['y']+objs[0]['h']*((1-box_prcentage)/2),
                       objs[0]['w']*box_prcentage, objs[0]['h']*box_prcentage]

    objs[0]['region'] = ['', '', '']  # reference object
    # [x,y,z]
    # x -> left[-1] middle[0] right[1]
    # y -> top[-1] middle[0] bottom[1]
    # z -> front[-1] middle[0] behind[1]

    for i in range(1, len(objs)):
        objs[i]['region'] = ['', '', '']
        # print(objs[i]['mid'])
        # for x
        if objs[i]['mid'][0] < shrinked_region[0]:
            objs[i]['region'][0] = 'left'
        elif objs[i]['mid'][0] > shrinked_region[0] + shrinked_region[2]:
            objs[i]['region'][0] = 'right'
        else:
            objs[i]['region'][0] = ''

        # for y
        if objs[i]['mid'][1] < shrinked_region[1]:
            objs[i]['region'][1] = 'top'
        elif objs[i]['mid'][1] > shrinked_region[1] + shrinked_region[3]:
            objs[i]['region'][1] = 'below'
        else:
            objs[i]['region'][1] = ''

        # for z
        try:
            if objs[i]['normsize'] > osr[objs[i]['cls']] + osr[objs[i]['cls']]*fb_percentage:
                objs[i]['region'][2] = 'front'
            elif objs[i]['normsize'] < osr[objs[i]['cls']] - osr[objs[i]['cls']]*fb_percentage:
                objs[i]['region'][2] = 'behind'
            else:
                objs[i]['region'][2] = ''
        except KeyError:
            objs[i]['region'][2] = ''

    # print(*[str(x['cls'])+' '+str(x['region']) for x in objs], sep='\n')

    # text generation
    text = ''
    text = f"There is a {objs[0]['cls']},"

    region_wise = {}

    for obj in objs[1:]:
        if obj['region'][2] != '':  # if it is frontleft it tells only front
            reg = obj['region'][2]
            if reg not in region_wise.keys():
                region_wise[reg] = []  # element = (cls, count)

            update_reg(region_wise[reg], obj['cls'])

        elif obj['region'][1] != '' or obj['region'][0] != '':
            reg = obj['region'][1]+obj['region'][0]
            if reg not in region_wise.keys():
                region_wise[reg] = []
            # count updation
            update_reg(region_wise[reg], obj['cls'])
        else:
            if 'front' not in region_wise.keys():
                region_wise['front'] = []
            update_reg(region_wise['front'], obj['cls'])

    for region in list(region_wise.items()):
        text += " on "+region[0]+" there is"
        for ob in region[1]:
            if ob[1] == 1:
                text += " a "+ob[0]+','
            else:
                text += f" {ob[1]} "+ob[0]+'s,'
    text = text[:-1]

    return text


def update_reg(reg, cls):
    for x in reg:
        if cls == x[0]:
            x[1] += 1
            return
    reg.append([cls, 1])
