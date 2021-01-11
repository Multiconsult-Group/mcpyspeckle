"""Module mc_pyspeckle
"""
import speckle
import speckle.schemas

def login_to_client_with_token_file(
    client_url=None, token_file=None
    ):
    """Function login_to_client_with_token_file
    """
    # Check input
    if not client_url:
        return None, None
    
    if not token_file:
        return None, None

    # Define client
    client = speckle.SpeckleApiClient(client_url)

    # Read API token from file
    with open(token_file, 'r') as read_this_file:
        api_token = read_this_file.readlines()[0]
    
    # Login with token
    login_status = client.login_with_token(api_token)

    return client, login_status

def get_parameter_list(
    client=None, stream_id=None
    ):
    """Function get_parameter_list
    """
    # Check input and find stream
    if not client:
        return None
    
    if not stream_id:
        return None
    else:
        stream = client.streams.get(stream_id)
    
    # Get parameter list from stream at client
    parameter_list = {}

    for stream_object in stream.objects:
        object_id = stream_object.id
        this_object = client.objects.get(object_id)
        
        parameter_list[this_object.name] = this_object.value
    
    return parameter_list

def create_parameter_objects(
    parameter_list=None
    ):
    """Function create_parameter_objects
    """
    new_objects = []

    # Create new objects based on dict with parameters
    for this_par in parameter_list:
        this_value = parameter_list[this_par]
        if type(this_value) == str:
            new_object = speckle.schemas.String()
        elif ((type(this_value) == int) or (type(this_value) == float)):
            new_object = speckle.schemas.Number()
        else:
            print(f'Type of parameter \'{this_par}\' not recognized as a Speckle type.')
            return None
        new_object.name = this_par
        new_object.value = this_value
        new_objects.append(new_object)
    
    return new_objects

def update_parameter_list(
    client=None, stream_id=None, parameter_list=None
    ):
    """Function update_parameter_list
    """
    # Check input
    if (not client) or (not stream_id) or (not parameter_list):
        return None

    # Find existing parameter list
    old_parameter_list = get_parameter_list(
        client=client, stream_id=stream_id
        )
    
    # Update parameter list
    parameter_list = {**old_parameter_list, **parameter_list}
    
    # Find stream and delete objects
    stream = client.streams.get(stream_id)
    for stream_object in stream.objects:
        object_id = stream_object.id
        this_object = client.objects.get(object_id)
        object_name = this_object.name
        this_object.value = parameter_list[object_name]
        client.objects.update(object_id, this_object)
        parameter_list.pop(object_name)

    # Create new objects
    new_objects = create_parameter_objects(
        parameter_list=parameter_list
        )
    
    for this_object in new_objects:
        object_placeholder = client.objects.create(this_object)
        stream.objects.extend(object_placeholder)

    # Update stream on client
    client.streams.update(stream_id, stream)

    return

def create_parameter_list(
    client=None, stream_name=None, parameter_list=None,
    force_create_and_delete=False
    ):
    """Function create_parameter_list
    """
    # Check input
    if (not client) or (not stream_name) or (not parameter_list):
        return None
    
    # Check if stream already exists
    for this_stream in client.streams.list():
        if stream_name == this_stream.name:
            print(f'Stream \'{stream_name}\' already exists on client.')
            if force_create_and_delete:
                client.streams.delete(this_stream.streamId)
                print(f'Deleted stream \'{this_stream.streamId}\'')
                pass
            else:
                return None
    
    # Create stream
    stream_data = {'name':stream_name}
    stream = client.streams.create(stream_data)
    stream_id = stream.streamId

    # Create objects in stream
    new_objects = create_parameter_objects(
        parameter_list=parameter_list
        )
    
    for this_object in new_objects:
        object_placeholder = client.objects.create(this_object)
        stream.objects.extend(object_placeholder)

    # Update stream on client
    client.streams.update(stream_id, stream)
    
    return stream_id