"""mcpyspeckle

A collection of functions extending the pyspeckle module. This module
contains the following functions:

    create_parameter_list
    create_parameter_objects
    get_parameter_list
    login_to_client_with_token_file
    update_parameter_list
"""
import speckle
import speckle.schemas

def login_to_client_with_token_file(
    client_url=None, token_file=None
    ):
    """Login to Speckle client with api token read from file.

    Keyword arguments
    -----------------
    client_url : str
        The url to the Speckle client. Defaults to None.
    
    token_file : str
        The name of the file containing the api token. Defaults to
        None.
    
    Returns
    -------
    client : speckle.SpeckleClient.SpeckleApiClient
        The Speckle client.
    
    login_status :
        The login status
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
    """Get list of parameters from a stream on a Speckle client.

    Keyword arguments
    -----------------
    client : speckle.SpeckleClient.SpeckleApiClient
        The Speckle client where the stream is located. Defaults to
        None.
    
    stream_id : str
        The ID of the stream containing the parameter list. Defaults
        to None.
    
    Returns
    -------
    parameter_list : dict
        A dictionary where keys and values are the object names and
        values found on the stream.
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
    """Create relevant Speckle objects based on a parameter list.

    Keyword arguments
    -----------------
    parameter_list : dict
        The dictionary of parameters to create Speckle objects based
        on. The dictionary key is used for the object name and the
        value is used to determine the object class. Defaults to None.
        The following classes are used based on the type of the value:

        str -> SpeckleString
        int -> SpeckleNumber
        float -> SpeckleNumber
    
    Returns
    -------
    new_objects : list
        A list of newly created objects.
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
    """Update a parameter list in a stream on a Speckle client.

    Keyword arguments
    -----------------
    client : speckle.SpeckleClient.SpeckleApiClient
        The Speckle client where the stream is located. Defaults to
        None.
    
    stream_id : str
        The ID of the stream containing the parameter list. Defaults
        to None.
    
    parameter_list : dict
        The dictionary of parameters to update. Only the parameters
        given in this dictionary are updated on the client. Defaults
        to None.
    
    Returns
    -------
    None
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
    """Create a parameter list on a Speckle client.

    Keyword arguments
    -----------------
    client : speckle.SpeckleClient.SpeckleApiClient
        The Speckle client where the stream will be located. Defaults
        to None.
    
    stream_name : str
        The name of the stream to create. Defaults to None.
    
    parameter_list : dict
        The dictionary of parameters to create. Defaults to None. See
        also function create_parameter_objects.

    force_create_and_delete : bool
        If a stream with the given name already exists on the client,
        delete it and create a new. Defaults to False.
    
    Returns
    -------
    stream_id : str
        The ID of the created stream.
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