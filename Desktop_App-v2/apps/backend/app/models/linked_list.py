import logging
from .question import QTypeOptions
from .node import Node

logger = logging.getLogger(__name__)

class LinkedList:
    def __init__(self):
        self.head:Node = None
        self.tail:Node = None
    
    def __eq__(self, other):
        if not isinstance(other, LinkedList):
            return False
        
        curr_self = self.head
        curr_other = other.head
        while curr_self and curr_other:
            if curr_self != curr_other:
                return False
            curr_self = curr_self.next
            curr_other = curr_other.next
        
        if curr_self != curr_other:
            return False
        
        return True


    def append(self, node:Node)->None:
        """Append node to end of linked list"""
        if self.head is None:
            self.head = node
            self.tail = node
            return
        #add node to the end of the linked list
        self.tail.next = node
        #set the prev of the Node
        node.prev = self.tail
        #update linked list tail
        self.tail = node
    def remove(self, node:Node)->None:
        """Remove a node from the linked list"""
        if node == self.head:
            self.head = node.next
            return
        
        prev:Node = node.prev
        prev.next = node.next
        if node != self.tail:   # if there is a node after the one being deleted
            prev.next.prev = prev
        
        # NOTE: fully unlinking node so that the garbace collector knows to get it
        node.next = None
        node.prev = None

    def printLL(self):
        """Print all of the linked list's node's details"""
        curr = self.head
        while curr:
            logger.info(curr.question, end="->")
            curr = curr.next
        logger.info("null")
    def returnLL(self):
        """Return a string of all the ll's node's details"""
        curr = self.head
        res = ""
        while curr:
            res += f"{curr.question.q_detail}->"
            curr = curr.next
        res += "null"
        return res
    def getByQType(self, val:str)->list[str]:
        """Search linked list for all nodes with a certain q_type
        
        Returns:
            found (list[str]): The q_details of the matching questions' q_type
        """
        found:list[str] = []
        curr:Node = self.head
        while curr:
            # logger.info("loop started")
            if curr.question.q_type == QTypeOptions(val):
                # logger.info("matched")
                found.append(curr.question.q_detail)
            curr = curr.next
        return found
    def getByDetail(self, val:str)->Node|None:
        """Search linked list by a node's question.q_detail"""
        ## NOTE: I feel like I could add some caching to this
        # function at a later date
        curr:Node = self.head
        while curr:
            if curr.question.q_detail == val:
                logger.info(f"matched {val}")
                return curr
            curr = curr.next
        return None
    def getByAddonDetail(self, val:str)->Node|None:
        """Search linked list by a node's addon.q_detail"""
        curr:Node = self.head
        while curr:
            if curr.addon:
                if curr.addon.q_detail == val:
                    return curr
            curr = curr.next
        return None
    def getByIdx(self, idx)->Node:
        """Search linked list by index"""
        curr:Node = self.head
        i = 0
        while curr:
            if i == idx:
                return curr
            i += 1
            curr = curr.next
        raise IndexError("Index out of range")
    def getAll(self) -> list[dict]:
        """Return a list of the dictionary forms of all the nodes"""
        res = []
        curr:Node = self.head
        while curr:
            res.append(curr.as_dict())
            curr = curr.next
        return res
    def getAllAnswers(self) -> list[str]:
        """Returns a list of all answers of all nodes in the linked list"""
        res = []
        curr:Node = self.head
        while curr:
            res.append(curr.answer)
            curr = curr.next
        return res
    def getAllDetails(self) -> list[str]:
        """Returns a list off all q_details of all questions in the linked list"""
        res = []
        curr:Node = self.head
        while curr:
            res.append(curr.question.q_detail)
            if curr.addon:
                res.append(curr.addon.q_detail)
            curr = curr.next
        return res
    def getAllQuestionDetails(self) -> list[str]:
        """Returns a list off all q_details of all questions in the linked list"""
        res = []
        curr:Node = self.head
        while curr:
            res.append(curr.question.q_detail)
            curr = curr.next
        return res
    def getQNum(self) -> int:
        """Get the number of questions in the linked list"""
        count = 0
        curr:Node = self.head
        while curr:
            count += 1
            if curr.addon is not None:
                count += 1
            curr = curr.next
        return count
    def clear(self):
        """Removes the linked list from memory"""
        # NOTE: With the head set to None, the old linked list is now no longer
        # referenced, and will be cleared by Python's garbage collection
        self.head = None