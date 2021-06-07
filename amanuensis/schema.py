from userportaldatamodel.schemas.schemas import (
    ReceiverSchema,
    MessageSchema,
    SearchSchema,
    ProjectSchema,
    RequestSchema,
    AttributesSchema,
    AttributeListSchema,
    AttributeListValueSchema,
    InputType
)



# from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
# from marshmallow_sqlalchemy.fields import Nested

# from amanuensis.models import Message, Receiver, InputType, AttributeListValue, AttributeList, Attributes

# class ReceiverSchema(SQLAlchemyAutoSchema):
#     class Meta:
#         model = Receiver

# class MessageSchema(SQLAlchemyAutoSchema):
#     receivers = Nested(ReceiverSchema, many=True) # , exclude=("message",)

#     class Meta:
#         model = Message
#         # include_relationships = True
#         # load_instance = True
#         include_fk = True


# class InputTypeSchema(SQLAlchemyAutoSchema):
# 	class Meta:
# 		model = InputType
	
# class AttributeListSchema(SQLAlchemyAutoSchema):
# 	input_type = Nested(InputTypeSchema)
# 	values = Nested(AttributeListValueSchema, many=True)

# 	class Meta:
# 		model = AttributeList		

# class AttributeListValueSchema(SQLAlchemyAutoSchema):
# 	input_type = Nested(InputTypeSchema)
# 	attribute_list = Nested(AttributeListSchema)

# 	class Meta:
# 		model = AttributeListValue

			
# class AttributesSchema(SQLAlchemyAutoSchema):
# 	attribute_list = Nested(AttributeListSchema)

# 	class Meta:
# 		model = Attributes
# 		include_fk = True
			
# 		