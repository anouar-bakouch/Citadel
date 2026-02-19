package parser

import "strconv"

// Node types
type Node interface {
	String() string
}

// Program is the root node
type Program struct {
	Functions []*Function
}

// Function represents a function definition
type Function struct {
	ReturnType string
	Name       string
	Params     []*Parameter
	Body       *Block
}

type Parameter struct {
	Type string
	Name string
}

// Statement types
type Statement interface {
	Node
	statementNode()
}

type Block struct {
	Statements []Statement
}

type VarDecl struct {
	Type  string
	Name  string
	Value Expression
}

type IfStatement struct {
	Condition Expression
	ThenBlock *Block
	ElseBlock *Block
}

type ReturnStatement struct {
	Value Expression
}

// Expression types
type Expression interface {
	Node
	expressionNode()
}

type Identifier struct {
	Name string
}

type IntLiteral struct {
	Value int
}

type BinaryOp struct {
	Left     Expression
	Operator string
	Right    Expression
}

// Implement interface methods
func (p *Program) String() string          { return "Program" }
func (f *Function) String() string         { return "Function: " + f.Name }
func (b *Block) statementNode()            {}
func (b *Block) String() string            { return "Block" }
func (v *VarDecl) statementNode()          {}
func (v *VarDecl) String() string          { return "VarDecl: " + v.Name }
func (i *IfStatement) statementNode()      {}
func (i *IfStatement) String() string      { return "IfStatement" }
func (r *ReturnStatement) statementNode()  {}
func (r *ReturnStatement) String() string  { return "ReturnStatement" }
func (id *Identifier) expressionNode()     {}
func (id *Identifier) String() string      { return id.Name }
func (il *IntLiteral) expressionNode()     {}
func (il *IntLiteral) String() string      { return strconv.Itoa(il.Value) }
func (b *BinaryOp) expressionNode()        {}
func (b *BinaryOp) String() string         { return "BinaryOp" }
