'''
Top contributors (to current version):
    - Christopher Lazarus
    - Shantanu Thakoor
    - Andrew Wu
    - Kyle Julian
    - Teruhiro Tagomori
    - Min Wu
    
This file is part of the Marabou project.
Copyright (c) 2017-2019 by the authors listed in the file AUTHORS
in the top-level source directory) and their institutional affiliations.
All rights reserved. See the file COPYING in the top-level source
directory for licensing information.

MarabouNetwork defines an abstract class that represents neural networks with piecewise linear constraints
'''

from maraboupy import MarabouCore
from maraboupy import MarabouUtils
from maraboupy.MarabouPythonic import *
import numpy as np


class MarabouNetwork:
    """Abstract class representing general Marabou network

    Attributes:
        numVars (int): Total number of variables to represent network
        equList (list of :class:`~maraboupy.MarabouUtils.Equation`): Network equations
        reluList (list of tuples): List of relu constraint tuples, where each tuple contains the backward and forward variables
        leakyReluList (list of tuples): List of leaky relu constraint tuples, where each tuple contains the backward and forward variables, and the slope
        sigmoidList (list of tuples): List of sigmoid constraint tuples, where each tuple contains the backward and forward variables
        maxList (list of tuples): List of max constraint tuples, where each tuple conatins the set of input variables and output variable
        absList (list of tuples): List of abs constraint tuples, where each tuple conatins the input variable and the output variable
        signList (list of tuples): List of sign constraint tuples, where each tuple conatins the input variable and the output variable
        lowerBounds (Dict[int, float]): Lower bounds of variables
        upperBounds (Dict[int, float]): Upper bounds of variables
        inputVars (list of numpy arrays): Input variables
        outputVars (list of numpy arrays): Output variables
    """
    def __init__(self):
        """Constructs a MarabouNetwork object and calls function to initialize
        """
        self.clear()

    def clear(self):
        """Reset values to represent empty network
        """
        self.numVars = 0
        self.equList = []
        self.additionalEquList = [] # used to store user defined equations
        self.reluList = []
        self.leakyReluList = []
        self.sigmoidList = []
        self.maxList = []
        self.softmaxList = []
        self.bilinearList = []
        self.absList = []
        self.signList = []
        self.disjunctionList = []
        self.lowerBounds = dict()
        self.upperBounds = dict()
        self.inputVars = []
        self.outputVars = []

    def clearProperty(self):
        """Clear the lower bounds and upper bounds map, and the self.additionEquList
        """
        self.lowerBounds.clear()
        self.upperBounds.clear()
        self.additionalEquList.clear()

    def getNewVariable(self):
        """Function to create a new variable

        Returns:
            (int): New variable number

        :meta private:
        """
        self.numVars += 1
        return self.numVars - 1

    def addEquation(self, x, isProperty=False):
        """Function to add new equation to the network

        Args:
            x (:class:`~maraboupy.MarabouUtils.Equation`): New equation to add
            isProperty (bool): If true, this constraint can be removed later by clearProperty() method
        """
        if isProperty:
            self.additionalEquList += [x]
        else:
            self.equList += [x]

    def setLowerBound(self, x, v):
        """Function to set lower bound for variable

        Args:
            x (int): Variable number to set
            v (float): Value representing lower bound
        """
        self.lowerBounds[x]=v

    def setUpperBound(self, x, v):
        """Function to set upper bound for variable

        Args:
            x (int): Variable number to set
            v (float): Value representing upper bound
        """
        self.upperBounds[x]=v

    def addRelu(self, v1, v2):
        """Function to add a new Relu constraint

        Args:
            v1 (int): Variable representing input of Relu
            v2 (int): Variable representing output of Relu
        """
        self.reluList += [(v1, v2)]

    def addLeakyRelu(self, v1, v2, slope):
        """Function to add a new Leaky Relu constraint

        Args:
            v1 (int): Variable representing input of Leaky Relu
            v2 (int): Variable representing output of Leaky Relu
            slope (float): Shope of the Leaky ReLU
        """
        self.leakyReluList += [(v1, v2, slope)]

    def addBilinear(self, v1, v2, v3):
        """Function to add a bilinear constraint to the network
        Args:
            v1 (int): Variable representing input1 of Bilinear
            v2 (int): Variable representing input2 of Bilinear
            v3 (int): Variable representing output of Bilinear
        """
        self.bilinearList += [(v1, v2, v3)]

    def addSigmoid(self, v1, v2):
        """Function to add a new Sigmoid constraint

        Args:
            v1 (int): Variable representing input of Sigmoid
            v2 (int): Variable representing output of Sigmoid
        """
        self.sigmoidList += [(v1, v2)]

    def addMaxConstraint(self, elements, v):
        """Function to add a new Max constraint

        Args:
            elements (set of int): Variable representing input to max constraint
            v (int): Variable representing output of max constraint
        """
        self.maxList += [(elements, v)]

    def addSoftmaxConstraint(self, inputs, outputs):
        """Function to add a new softmax constraint

        Args:
            inputs (set of int): Variable representing input to max constraint
            outputs (set of int): Variables representing outputs of max constraint
        """
        self.softmaxList += [(inputs, outputs)]

    def addAbsConstraint(self, b, f):
        """Function to add a new Abs constraint

        Args:
            b (int): Variable representing input of the Abs constraint
            f (int): Variable representing output of the Abs constraint
        """
        self.absList += [(b, f)]

    def addSignConstraint(self, b, f):
        """Function to add a new Sign constraint

        Args:
            b (int): Variable representing input of Sign
            f (int): Variable representing output of Sign
        """
        self.signList += [(b, f)]

    def addDisjunctionConstraint(self, disjuncts):
        """Function to add a new Disjunction constraint

        Args:
            disjuncts (list of list of Equations): Each inner list represents a disjunct
        """
        self.disjunctionList.append(disjuncts)

    def lowerBoundExists(self, x):
        """Function to check whether lower bound for a variable is known

        Args:
            x (int): Variable to check
        """
        return x in self.lowerBounds

    def upperBoundExists(self, x):
        """Function to check whether upper bound for a variable is known

        Args:
            x (int): Variable to check
        """
        return x in self.upperBounds

    def addEquality(self, vars, coeffs, scalar, isProperty=False):
        """Function to add equality constraint to network

        .. math::
            \sum_i vars_i * coeffs_i = scalar

        Args:
            vars (list of int): Variable numbers
            coeffs (list of float): Coefficients
            scalar (float): Right hand side constant of equation
            isProperty (bool): If true, this constraint can be removed later by clearProperty() method
        """
        assert len(vars)==len(coeffs)
        e = MarabouUtils.Equation()
        for i in range(len(vars)):
            e.addAddend(coeffs[i], vars[i])
        e.setScalar(scalar)
        self.addEquation(e, isProperty)

    def addInequality(self, vars, coeffs, scalar, isProperty=False):
        """Function to add inequality constraint to network

        .. math::
            \sum_i vars_i * coeffs_i \le scalar

        Args:
            vars (list of int): Variable numbers
            coeffs (list of float): Coefficients
            scalar (float): Right hand side constant of inequality
            isProperty (bool): If true, this constraint can be removed later by clearProperty() method
        """
        assert len(vars)==len(coeffs)
        e = MarabouUtils.Equation(MarabouCore.Equation.LE)
        for i in range(len(vars)):
            e.addAddend(coeffs[i], vars[i])
        e.setScalar(scalar)
        self.addEquation(e, isProperty)

    def getMarabouQuery(self):
        """Function to convert network into Marabou InputQuery

        Returns:
            :class:`~maraboupy.MarabouCore.InputQuery`
        """
        ipq = MarabouCore.InputQuery()
        ipq.setNumberOfVariables(self.numVars)

        i = 0
        for inputVarArray in self.inputVars:
            for inputVar in inputVarArray.flatten():
                ipq.markInputVariable(inputVar, i)
                i+=1

        i = 0
        for outputVarArray in self.outputVars:
            for outputVar in outputVarArray.flatten():
                ipq.markOutputVariable(outputVar, i)
                i+=1

        for e in self.equList:
            eq = MarabouCore.Equation(e.EquationType)
            for (c, v) in e.addendList:
                assert v < self.numVars
                eq.addAddend(c, v)
            eq.setScalar(e.scalar)
            ipq.addEquation(eq)

        for e in self.additionalEquList:
            eq = MarabouCore.Equation(e.EquationType)
            for (c, v) in e.addendList:
                assert v < self.numVars
                eq.addAddend(c, v)
            eq.setScalar(e.scalar)
            ipq.addEquation(eq)

        for r in self.reluList:
            assert r[1] < self.numVars and r[0] < self.numVars
            MarabouCore.addReluConstraint(ipq, r[0], r[1])

        for r in self.leakyReluList:
            assert r[1] < self.numVars and r[0] < self.numVars
            assert(r[2] > 0 and r[2] < 1)
            MarabouCore.addLeakyReluConstraint(ipq, r[0], r[1], r[2])

        for r in self.bilinearList:
            assert r[2] < self.numVars and r[1] < self.numVars and r[0] < self.numVars
            MarabouCore.addBilinearConstraint(ipq, r[0], r[1], r[2])

        for r in self.sigmoidList:
            assert r[1] < self.numVars and r[0] < self.numVars
            MarabouCore.addSigmoidConstraint(ipq, r[0], r[1])

        for m in self.maxList:
            assert m[1] < self.numVars
            for e in m[0]:
                assert e < self.numVars
            MarabouCore.addMaxConstraint(ipq, m[0], m[1])

        for m in self.softmaxList:
            for e in m[1]:
                assert e < self.numVars
            for e in m[0]:
                assert e < self.numVars
            MarabouCore.addSoftmaxConstraint(ipq, m[0], m[1])

        for b, f in self.absList:
            MarabouCore.addAbsConstraint(ipq, b, f)

        for b, f in self.signList:
            MarabouCore.addSignConstraint(ipq, b, f)

        for disjunction in self.disjunctionList:
            converted_disjunction = []
            for disjunct in disjunction:
                converted_disjunct = []
                for e in disjunct:
                    eq = MarabouCore.Equation(e.EquationType)
                    for (c, v) in e.addendList:
                        assert v < self.numVars
                        eq.addAddend(c, v)
                    eq.setScalar(e.scalar)
                    converted_disjunct.append(eq)
                converted_disjunction.append(converted_disjunct)
            MarabouCore.addDisjunctionConstraint(ipq, converted_disjunction)

        for l in self.lowerBounds:
            assert l < self.numVars
            ipq.setLowerBound(l, self.lowerBounds[l])

        for u in self.upperBounds:
            assert u < self.numVars
            ipq.setUpperBound(u, self.upperBounds[u])

        return ipq

    def solve(self, filename="", verbose=True, options=None, propertyFilename=""):
        """Function to solve query represented by this network

        Args:
            filename (string): Path for redirecting output
            verbose (bool): If true, print out solution after solve finishes
            options (:class:`~maraboupy.MarabouCore.Options`): Object for specifying Marabou options, defaults to None
            propertyFilename(string): Path for property file

        Returns:
            (tuple): tuple containing:
                - exitCode (str): A string representing the exit code (sat/unsat/TIMEOUT/ERROR/UNKNOWN/QUIT_REQUESTED).
                - vals (Dict[int, float]): Empty dictionary if UNSAT, otherwise a dictionary of SATisfying values for variables
                - stats (:class:`~maraboupy.MarabouCore.Statistics`): A Statistics object to how Marabou performed
        """
        ipq = self.getMarabouQuery()
        if propertyFilename:
            MarabouCore.loadProperty(ipq, propertyFilename)
        if options == None:
            options = MarabouCore.Options()
        exitCode, vals, stats = MarabouCore.solve(ipq, options, str(filename))
        if verbose:
            print(exitCode)
            if exitCode == "sat":
                for j in range(len(self.inputVars)):
                    for i in range(self.inputVars[j].size):
                        print("input {} = {}".format(i, vals[self.inputVars[j].item(i)]))

                for j in range(len(self.outputVars)):
                    for i in range(self.outputVars[j].size):
                        print("output {} = {}".format(i, vals[self.outputVars[j].item(i)]))

        return [exitCode, vals, stats]


    def calculateBounds(self, filename="", verbose=True, options=None):
        """Function to calculate bounds represented by this network

        Args:
            filename (string): Path for redirecting output
            verbose (bool): If true, print out output bounds after calculation finishes
            options (:class:`~maraboupy.MarabouCore.Options`): Object for specifying Marabou options, defaults to None

        Returns:
            (tuple): tuple containing:
                - exitCode (str): A string representing the exit code. Only unsat can be return.
                - bounds (Dict[int, tuple]): Empty dictionary if UNSAT, otherwise a dictionary of bounds for output variables
                - stats (:class:`~maraboupy.MarabouCore.Statistics`): A Statistics object to how Marabou performed
        """
        ipq = self.getMarabouQuery()
        if options == None:
            options = MarabouCore.Options()
        exitCode, bounds, stats = MarabouCore.calculateBounds(ipq, options, str(filename))
        
        if verbose:
            print(exitCode)
            if exitCode == "":
                for j in range(len(self.outputVars)):
                    for i in range(self.outputVars[j].size):
                        print("output bounds {} = {}".format(i, bounds[self.outputVars[j].item(i)]))

        return [exitCode, bounds, stats]

    def evaluateLocalRobustness(self, input, epsilon, originalClass, verbose=True, options=None, targetClass=None):
        """Function evaluating a specific input is a local robustness within the scope of epslion

        Args:
            input (numpy.ndarray): Target input
            epsilon (float): L-inf norm of purturbation
            originalClass (int): Output class of a target input
            verbose (bool): If true, print out solution after solve finishes
            options (:class:`~maraboupy.MarabouCore.Options`): Object for specifying Marabou options, defaults to None
            targetClass (int): If set, find a feasible solution with which the value of targetClass is max within outputs.

        Returns:
            (tuple): tuple containing:
                - vals (Dict[int, float]): Empty dictionary if UNSAT, otherwise a dictionary of SATisfying values for variables
                - stats (:class:`~maraboupy.MarabouCore.Statistics`): A Statistics object to how Marabou performed
                - maxClass (int): Output class which value is max within outputs if SAT.
        """
        inputVars = None
        if (type(self.inputVars) is list):
            if (len(self.inputVars) != 1):
                raise NotImplementedError("Operation for %d inputs is not implemented" % len(self.inputVars))
            inputVars = self.inputVars[0][0]
        elif (type(self.inputVars) is np.ndarray):
            inputVars = self.inputVars[0]
        else:
            err_msg = "Unpexpected type of input vars."
            raise RuntimeError(err_msg)

        if inputVars.shape != input.shape:
            raise RuntimeError("Input shape of the model should be same as the input shape\n input shape of the model: {0}, shape of the input: {1}".format(inputVars.shape, input.shape))

        if (type(self.outputVars) is list):
            if (len(self.outputVars) != 1):
                raise NotImplementedError("Operation for %d outputs is not implemented" % len(self.outputVars))
        elif (type(self.outputVars) is np.ndarray):
            if (len(self.outputVars) != 1):
                raise NotImplementedError("Operation for %d outputs is not implemented" % len(self.outputVars))
        else:
            err_msg = "Unpexpected type of output vars."
            raise RuntimeError(err_msg)

        if options == None:
            options = MarabouCore.Options()

        # Add constratins to all input nodes
        flattenInputVars = inputVars.flatten()
        flattenInput = input.flatten()
        for i in range(flattenInput.size):
            self.setLowerBound(flattenInputVars[i], flattenInput[i] - epsilon)
            self.setUpperBound(flattenInputVars[i], flattenInput[i] + epsilon)
        
        maxClass = None
        outputStartIndex = self.outputVars[0][0][0]

        if targetClass is None:
            outputLayerSize = len(self.outputVars[0][0])
            # loop for all of output classes except for original class
            for outputLayerIndex in range(outputLayerSize):
                if outputLayerIndex != originalClass:
                    self.addMaxConstraint(set([outputStartIndex + outputLayerIndex, outputStartIndex + originalClass]), 
                        outputStartIndex + outputLayerIndex)
                    exitCode, vals, stats = self.solve(options = options)
                    if (stats.hasTimedOut()):
                        break
                    elif (len(vals) > 0):
                        maxClass = outputLayerIndex
                        break
        else:
            self.addMaxConstraint(set(self.outputVars[0][0]), outputStartIndex + targetClass)
            exitCode, vals, stats = self.solve(options = options)
            if verbose:
                if not stats.hasTimedOut() and len(vals) > 0:
                    maxClass = targetClass
        
        # print timeout, or feasible inputs and outputs if verbose is on.
        if verbose:
            if stats.hasTimedOut():
                print("TO")
            elif len(vals) > 0:
                print("sat")
                for j in range(len(self.inputVars[0])):
                    for i in range(self.inputVars[0][j].size):
                        print("input {} = {}".format(i, vals[self.inputVars[0][j].item(i)]))

                for j in range(len(self.outputVars[0])):
                    for i in range(self.outputVars[0][j].size):
                        print("output {} = {}".format(i, vals[self.outputVars[0][j].item(i)]))

        return [vals, stats, maxClass]

    def saveQuery(self, filename=""):
        """Serializes the inputQuery in the given filename

        Args:
            filename: (string) file to write serialized inputQuery
        """
        ipq = self.getMarabouQuery()
        MarabouCore.saveQuery(ipq, str(filename))

    def evaluateWithMarabou(self, inputValues, filename="evaluateWithMarabou.log", options=None):
        """Function to evaluate network at a given point using Marabou as solver

        Args:
            inputValues (list of np arrays): Inputs to evaluate
            filename (str): Path to redirect output if using Marabou solver, defaults to "evaluateWithMarabou.log"
            options (:class:`~maraboupy.MarabouCore.Options`): Object for specifying Marabou options, defaults to None

        Returns:
            (list of np arrays): Values representing the outputs of the network or None if system is UNSAT
        """
        # Make sure inputValues is a list of np arrays and not list of lists
        inputValues = [np.array(inVal) for inVal in inputValues]
        
        inputVars = self.inputVars # list of numpy arrays
        outputVars = self.outputVars # list of numpy arrays

        inputDict = dict()
        inputVarList = np.concatenate([inVar.flatten() for inVar in inputVars], axis=-1).flatten()
        inputValList = np.concatenate([inVal.flatten() for inVal in inputValues]).flatten()
        assignList = zip(inputVarList, inputValList)
        for x in assignList:
            inputDict[x[0]] = x[1]

        ipq = self.getMarabouQuery()
        for k in inputDict:
            ipq.setLowerBound(k, inputDict[k])
            ipq.setUpperBound(k, inputDict[k])

        if options == None:
            options = MarabouCore.Options()
        exitCode, outputDict, _ = MarabouCore.solve(ipq, options, str(filename))

        # When the query is UNSAT an empty dictionary is returned
        if outputDict == {}:
            return None

        outputValues = [outVars.reshape(-1).astype(np.float64) for outVars in outputVars]
        for i in range(len(outputValues)):
            for j in range(len(outputValues[i])):
                outputValues[i][j] = outputDict[outputValues[i][j]]
            outputValues[i] = outputValues[i].reshape(outputVars[i].shape)
        return outputValues

    def evaluate(self, inputValues, useMarabou=True, options=None, filename="evaluateWithMarabou.log"):
        """Function to evaluate network at a given point

        Args:
            inputValues (list of np arrays): Inputs to evaluate
            useMarabou (bool): Whether to use Marabou solver or TF/ONNX, defaults to True
            options (:class:`~maraboupy.MarabouCore.Options`): Object for specifying Marabou options, defaults to None
            filename (str): Path to redirect output if using Marabou solver, defaults to "evaluateWithMarabou.log"

        Returns:
            (list of np arrays): Values representing the outputs of the network or None if output cannot be computed
        """
        if useMarabou:
            return self.evaluateWithMarabou(inputValues, filename=filename, options=options)
        if not useMarabou:
            return self.evaluateWithoutMarabou(inputValues)

    def findError(self, inputValues, options=None, filename="evaluateWithMarabou.log"):
        """Function to find error between Marabou solver and TF/Nnet at a given point

        Args:
            inputValues (list of np arrays): Input values to evaluate
            options (:class:`~maraboupy.MarabouCore.Options`) Object for specifying Marabou options, defaults to None
            filename (str): Path to redirect output if using Marabou solver, defaults to "evaluateWithMarabou.log"

        Returns:
            (list of np arrays): Values representing the error in each output variable
        """
        outMar = self.evaluate(inputValues, useMarabou=True, options=options, filename=filename)
        outNotMar = self.evaluate(inputValues, useMarabou=False, options=options, filename=filename)
        assert len(outMar) == len(outNotMar)
        err = [np.abs(outMar[i] - outNotMar[i]) for i in range(len(outMar))]
        return err

    def isEqualTo(self, network):
        """
        Add a comparison between two Marabou networks and all their attributes.

        :param network: the other Marabou network to be compared with.
        :return: True if these two networks and all their attributes are identical; False if not.
        """
        equivalence = True
        if self.numVars != network.numVars \
                or self.reluList != network.reluList \
                or self.sigmoidList != network.sigmoidList \
                or self.maxList != network.maxList \
                or self.absList != network.absList \
                or self.signList != network.signList \
                or self.disjunctionList != network.disjunctionList \
                or self.lowerBounds != network.lowerBounds \
                or self.upperBounds != network.upperBounds:
            equivalence = False
        for equation1, equation2 in zip(self.equList, network.equList):
            if not equation1.isEqualTo(equation2):
                equivalence = False
        for inputvars1, inputvars2 in zip(self.inputVars, network.inputVars):
            if (inputvars1.flatten() != inputvars2.flatten()).any():
                equivalence = False
        for outputVars1, outputVars2 in zip(self.outputVars, network.outputVars):
            if (outputVars1.flatten() != outputVars1.flatten()).any():
                equivalence = False
        return equivalence

    def addConstraint(self, constraint: VarConstraint):
        """
        Support the Pythonic API to add constraints to the neurons in the Marabou network.

        :param constraint: an instance of the VarConstraint class, which comprises various neuron constraints.
        :return: delegate various constraints into lower/upper bounds and equality/inequality.
        """
        vars = list(constraint.combination.varCoeffs)
        coeffs = [constraint.combination.varCoeffs[i] for i in vars]
        if constraint.lowerBound is not None:
            self.setLowerBound(vars[0], constraint.lowerBound)
        elif constraint.upperBound is not None:
            self.setUpperBound(vars[0], constraint.upperBound)
        else:
            if constraint.isEquality:
                self.addEquality(vars, coeffs, - constraint.combination.scalar)
            else:
                self.addInequality(vars, coeffs, - constraint.combination.scalar)
