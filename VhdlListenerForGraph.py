from antlr4 import *
from antlr_generated.VhdlListener import VhdlListener
from vhdl_model.Component import Component
from vhdl_model.Process import Process
from deque.Deque import Deque
from collections import namedtuple
import logging


class VhdlListenerForGraph(VhdlListener):

    def __init__(self):
        logging.basicConfig(filename='runtime.log',
                            filemode='w',
                            level=logging.DEBUG)
        self.parsing_stack = Deque()
        # TODO maybe a hashmap would be better here ?
        self.instances_list = []
        self.processes_list = []

    # Component instantiation statement
    def enterComponent_instantiation_statement(self, ctx):
        # Create an empty Component instance and add it to the parsing stack
        self.parsing_stack.push(Component())
        logging.info("PUSH Component")

    def exitComponent_instantiation_statement(self, ctx):
        # Pop the parsing stack and add the element to the components list
        self.instances_list.append(self.parsing_stack.pop())
        logging.info("POP  Component")

    # Label colon
    def enterLabel_colon(self, ctx):
        self.parsing_stack.push(namedtuple("Label", "identifier"))
        logging.info("PUSH Label")

    def exitLabel_colon(self, ctx):
        label = self.parsing_stack.pop()
        self.parsing_stack.preview_top().add_label(label.identifier)
        logging.info("POP  Label")

    # Instantiation unit
    def enterInstantiated_unit(self, ctx):
        self.parsing_stack.push(namedtuple("InstantiatedUnit", "identifier"))
        logging.info("PUSH InstantiatedUnit")

    def exitInstantiated_unit(self, ctx):
        instantiated_unit = self.parsing_stack.pop()
        self.parsing_stack.preview_top().add_name(instantiated_unit.identifier)
        logging.info("POP  InstantiatedUnit")

    # Name
    def enterName(self, ctx):
        self.parsing_stack.push(namedtuple("Name", "identifier"))
        logging.info("PUSH Name")

    def exitName(self, ctx):
        name = self.parsing_stack.pop()
        # For now, assume it's an instantiated unit
        if isinstance(self.parsing_stack.preview_top(), tuple):
            self.parsing_stack.preview_top().identifier = name.identifier
        logging.info("POP  Name")

    # Identifier
    def enterIdentifier(self, ctx):
        self.parsing_stack.preview_top().identifier = ctx.BASIC_IDENTIFIER()
        logging.info("SET  identifier {}".format(ctx.BASIC_IDENTIFIER()))

    def exitIdentifier(self, ctx):
        pass

    # Port map aspect
    def enterPort_map_aspect(self, ctx):
        self.parsing_stack.push(namedtuple("PortMap", "associations"))
        self.parsing_stack.preview_top().associations = []
        logging.info("PUSH PortMap")

    def exitPort_map_aspect(self, ctx):
        port_map = self.parsing_stack.pop()
        # TODO add port_map property to Component as a list of associations
        self.parsing_stack.preview_top().port_map = port_map
        logging.info("POP  PortMap")

    # Association element
    def enterAssociation_element(self, ctx):
        self.parsing_stack.push(namedtuple("Association",
                                           ["formal", "actual"]))
        logging.info("PUSH Association")

    def exitAssociation_element(self, ctx):
        association = self.parsing_stack.pop()
        if isinstance(self.parsing_stack.preview_top(), Component):
            self.parsing_stack.preview_top().associations.append(association)
        logging.info("POP  Association")

    # Formal part
    def enterFormal_part(self, ctx):
        self.parsing_stack.push(namedtuple("Formal", "identifier"))
        logging.info("PUSH Formal")

    def exitFormal_part(self, ctx):
        formal_part = self.parsing_stack.pop()
        self.parsing_stack.preview_top().formal = formal_part.identifier
        logging.info("POP  Formal")

    # Actual part
    def enterActual_part(self, ctx):
        self.parsing_stack.push(namedtuple("Actual", "identifier"))
        logging.info("PUSH Actual")

    def exitActual_part(self, ctx):
        actual_part = self.parsing_stack.pop()
        self.parsing_stack.preview_top().actual = actual_part.identifier
        logging.info("POP  Actual")

    # Process statement
    def enterProcess_statement(self, ctx):
        self.parsing_stack.push(Process())
        logging.info("PUSH Process")

    def exitProcess_statement(self, ctx):
        self.instances_list.append(self.parsing_stack.pop())
        logging.info("POP  Process")
