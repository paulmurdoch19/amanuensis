"""
This module checks that both loaded dictionary and models
have required attributes for amanuensis. It's called by
amanuensis.blueprint.create_blueprint to make sure that datamodelutils
and dictionaryutils is correctly initialized.
example:

.. code-block:: python
    amanuensis.sanity_checks.validate()
"""


#: The data dictionary must implement these attributes.
# DICTIONARY_REQUIRED_ATTRS = ["resolvers", "schema"]




def validate():
    """
    Check that both loaded dictionary and models have
    required attributes for amanuensis
    """
    # check_attributes(dictionary, DICTIONARY_REQUIRED_ATTRS)
    print("ciao TODO")


def check_attributes(module, required_attrs):
    """
    Check if a module have a list of required attributes
    module: target module
    required_attrs (str[]): a list of required attributes

    Return:
        None
    """
    for required_attr in required_attrs:
        if not hasattr(module, required_attr):
            raise ValueError("given dictionary does not define " + required_attr)
