#import mtconnect
from mtconnect import MTConnect

def mtconnect_adapter(variable_instance):
    return MTConnect(loc='config/device.xml')


import asyncio
from asyncua import ua, Server

async def opcua_server(variable_instance):
    logger = variable_instance.logger_class.logger
    logger.info("Starting Opcua Server")
# setup our server
    server = Server()
    await server.init()

    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://pi{}.rpiforge.eng.rpi.edu".format(variable_instance.printer_id)
    idx = await server.register_namespace(uri)

    logger.info("Opening opcua on port 4840")


    # create device type
#
# This is currently hard coded like mtconnect based on a config file
#

    device_type = await server.nodes.base_object_type.add_object_type(idx, "PrusaPrinter")

    await (await device_type.add_property(idx, "device_id", str(variable_instance.printer_id))).set_modelling_rule(True)
    await (await device_type.add_property(idx, "status", "na", ua.VariantType.String)).set_modelling_rule(True)

    tool_obj = await device_type.add_object(idx, "ToolTemperature")
    await tool_obj.set_modelling_rule(True)
    await (await tool_obj.add_variable(idx, "temp", -1.0, ua.VariantType.Double)).set_modelling_rule(True)
    await (await tool_obj.add_variable(idx, "target", -1.0, ua.VariantType.Double)).set_modelling_rule(True)
    
    bed_obj = await device_type.add_object(idx, "BedTemperature")
    await bed_obj.set_modelling_rule(True)
    await (await bed_obj.add_variable(idx, "temp", -1.0, ua.VariantType.Double)).set_modelling_rule(True)
    await (await bed_obj.add_variable(idx, "target", -1.0, ua.VariantType.Double)).set_modelling_rule(True)   

    device = await server.nodes.objects.add_object(idx,variable_instance.name , device_type)

    opcua_ref = {}
    opcua_ref["tool0-temp"] =  await device.get_child([f"{idx}:ToolTemperature", f"{idx}:temp"]) 
    opcua_ref["tool0-target"] =  await device.get_child([f"{idx}:ToolTemperature", f"{idx}:target"]) 
    opcua_ref["bed-temp"] =  await device.get_child([f"{idx}:BedTemperature", f"{idx}:temp"]) 
    opcua_ref["bed-target"] = await device.get_child([f"{idx}:BedTemperature", f"{idx}:target"]) 
    opcua_ref["status"] = await device.get_child([f"{idx}:status"]) 

    variable_instance.opcua_ref = opcua_ref
    
    async with server:
        while True:
            await asyncio.sleep(1)

def asyncio_helper(loop, variable):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(opcua_server(variable))

import threading
def start_opcua_adapter(variable):
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=asyncio_helper, args=(loop,variable))
    t.start()