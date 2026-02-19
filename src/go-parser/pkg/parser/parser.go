package parser

import (
	"fmt"
	"llvm-security-parser/pkg/lexer"
	"strconv"
)

type Parser struct {
	lex     *lexer.Lexer
	current lexer.Token
	peek    lexer.Token
}

func New(lex *lexer.Lexer) *Parser {
	p := &Parser{lex: lex}
	p.advance()
	p.advance()
	return p
}

func (p *Parser) advance() {
	p.current = p.peek
	p.peek = p.lex.NextToken()
}

func (p *Parser) expect(tokenType lexer.TokenType) error {
	if p.current.Type != tokenType {
		return fmt.Errorf("expected token %d, got %d", tokenType, p.current.Type)
	}
	p.advance()
	return nil
}

// Parse the entire program
func (p *Parser) ParseProgram() (*Program, error) {
	program := &Program{}
	
	for p.current.Type != lexer.EOF {
		fn, err := p.parseFunction()
		if err != nil {
			return nil, err
		}
		program.Functions = append(program.Functions, fn)
	}
	
	return program, nil
}

// Parse a function
func (p *Parser) parseFunction() (*Function, error) {
	fn := &Function{}
	
	// Return type
	if p.current.Type != lexer.INT {
		return nil, fmt.Errorf("expected return type, got %s", p.current.Literal)
	}
	fn.ReturnType = p.current.Literal
	p.advance()
	
	// Function name
	if p.current.Type != lexer.IDENTIFIER {
		return nil, fmt.Errorf("expected function name")
	}
	fn.Name = p.current.Literal
	p.advance()
	
	// Parameters
	if err := p.expect(lexer.LPAREN); err != nil {
		return nil, err
	}
	
	// Parse parameters (simplified: only int type)
	for p.current.Type != lexer.RPAREN {
		if p.current.Type == lexer.INT {
			p.advance()
			if p.current.Type == lexer.IDENTIFIER {
				param := &Parameter{Type: "int", Name: p.current.Literal}
				fn.Params = append(fn.Params, param)
				p.advance()
			}
			if p.current.Type == lexer.COMMA {
				p.advance()
			}
		}
	}
	p.advance() // consume )
	
	// Body
	body, err := p.parseBlock()
	if err != nil {
		return nil, err
	}
	fn.Body = body
	
	return fn, nil
}

// Parse a block
func (p *Parser) parseBlock() (*Block, error) {
	block := &Block{}
	
	if err := p.expect(lexer.LBRACE); err != nil {
		return nil, err
	}
	
	for p.current.Type != lexer.RBRACE && p.current.Type != lexer.EOF {
		stmt, err := p.parseStatement()
		if err != nil {
			return nil, err
		}
		block.Statements = append(block.Statements, stmt)
	}
	
	p.advance() // consume }
	return block, nil
}

// Parse a statement
func (p *Parser) parseStatement() (Statement, error) {
	switch p.current.Type {
	case lexer.INT:
		return p.parseVarDecl()
	case lexer.IF:
		return p.parseIfStatement()
	case lexer.RETURN:
		return p.parseReturnStatement()
	default:
		return nil, fmt.Errorf("unexpected token: %s", p.current.Literal)
	}
}

// Parse variable declaration
func (p *Parser) parseVarDecl() (*VarDecl, error) {
	decl := &VarDecl{}
	decl.Type = p.current.Literal
	p.advance()
	
	if p.current.Type != lexer.IDENTIFIER {
		return nil, fmt.Errorf("expected identifier")
	}
	decl.Name = p.current.Literal
	p.advance()
	
	if p.current.Type == lexer.EQUALS {
		p.advance()
		expr, err := p.parseExpression()
		if err != nil {
			return nil, err
		}
		decl.Value = expr
	}
	
	p.expect(lexer.SEMICOLON)
	return decl, nil
}

// Parse if statement
func (p *Parser) parseIfStatement() (*IfStatement, error) {
	stmt := &IfStatement{}
	p.advance() // consume 'if'
	
	p.expect(lexer.LPAREN)
	condition, err := p.parseExpression()
	if err != nil {
		return nil, err
	}
	stmt.Condition = condition
	p.expect(lexer.RPAREN)
	
	thenBlock, err := p.parseBlock()
	if err != nil {
		return nil, err
	}
	stmt.ThenBlock = thenBlock
	
	return stmt, nil
}

// Parse return statement
func (p *Parser) parseReturnStatement() (*ReturnStatement, error) {
	stmt := &ReturnStatement{}
	p.advance() // consume 'return'
	
	expr, err := p.parseExpression()
	if err != nil {
		return nil, err
	}
	stmt.Value = expr
	
	p.expect(lexer.SEMICOLON)
	return stmt, nil
}

// Parse expression (simplified)
func (p *Parser) parseExpression() (Expression, error) {
	left, err := p.parsePrimary()
	if err != nil {
		return nil, err
	}
	
	// Check for binary operators
	if p.current.Type == lexer.EQUAL_EQUAL || p.current.Type == lexer.PLUS ||
		p.current.Type == lexer.GREATER || p.current.Type == lexer.LESS {
		op := p.current.Literal
		p.advance()
		
		right, err := p.parseExpression()
		if err != nil {
			return nil, err
		}
		
		return &BinaryOp{Left: left, Operator: op, Right: right}, nil
	}
	
	return left, nil
}

// Parse primary expression
func (p *Parser) parsePrimary() (Expression, error) {
	switch p.current.Type {
	case lexer.IDENTIFIER:
		name := p.current.Literal
		p.advance()
		return &Identifier{Name: name}, nil
	case lexer.NUMBER:
		val, _ := strconv.Atoi(p.current.Literal)
		p.advance()
		return &IntLiteral{Value: val}, nil
	default:
		return nil, fmt.Errorf("unexpected token in expression: %s", p.current.Literal)
	}
}
