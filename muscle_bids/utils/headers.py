def headers_to_dicts(header_list):
    if type(header_list) != list:
        header_list = header_list.squeeze().tolist()

    json_header_list = []
    for h in header_list:
        json_header_list.append({'meta': h.file_meta.to_json_dict(), 'header': h.to_json_dict()})

    # compress json header list
    compressed_meta = {}
    compressed_header = {}

    def process_tag(tag, content, index, dest_dictionary):
        if tag not in dest_dictionary:
            dest_dictionary[tag] = content
            return
        existing_content = dest_dictionary[tag]
        if content == existing_content: return # do nothing if the content is the same as the other slices
        # append to existing content
        #print(existing_content)

        value_tag = 'Value'
        if 'InlineBinary' in existing_content: value_tag = 'InlineBinary'
        if 'BulkDataURI' in existing_content: value_tag = 'BulkDataURI'

        if 'isList' not in existing_content: # content is already a list
            existing_content['isList'] = True
            existing_content[value_tag] = [existing_content[value_tag]] * (index - 1)  # replicate content until now

        existing_content[value_tag].append(content[value_tag])

    for i, element in enumerate(json_header_list):
        for tag, content in element['header'].items():
            process_tag(tag, content, i, compressed_header)
        for tag, content in element['meta'].items():
            process_tag(tag, content, i, compressed_meta)

    return compressed_meta, compressed_header
