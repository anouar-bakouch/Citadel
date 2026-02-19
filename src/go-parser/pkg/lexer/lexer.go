package lexer

import (
	"unicode"
)

type TokenType int

const (
	// Keywords
	INT TokenType = iota
	IF
	RETURN
	
	// Identifiers and literals
	IDENTIFIER
	NUMBER
	
	// Operators
	EQUALS
	EQUAL_EQUAL  // ==
	PLUS
	MINUS
	GREATER
	LESS
	
	// Delimiters
	LPAREN
	RPAREN
	LBRACE
	RBRACE
	SEMICOLON
	COMMA
	
	// Special
	EOF
	ILLEGAL
)

type Token struct {
	Type    TokenType
	Literal string
}

type Lexer struct {
	input   string
	pos     int
	current byte
}

func New(input string) *Lexer {
	l := &Lexer{input: input}
	if len(input) > 0 {
		l.current = input[0]
	}
	return l
}

func (l *Lexer) advance() {
	l.pos++
	if l.pos >= len(l.input) {
		l.current = 0
	} else {
		l.current = l.input[l.pos]
	}
}

func (l *Lexer) peek() byte {
	if l.pos+1 >= len(l.input) {
		return 0
	}
	return l.input[l.pos+1]
}

func (l *Lexer) skipWhitespace() {
	for l.current == ' ' || l.current == '\t' || l.current == '\n' || l.current == '\r' {
		l.advance()
	}
}

func (l *Lexer) readIdentifier() string {
	start := l.pos
	for unicode.IsLetter(rune(l.current)) || unicode.IsDigit(rune(l.current)) || l.current == '_' {
		l.advance()
	}
	return l.input[start:l.pos]
}

func (l *Lexer) readNumber() string {
	start := l.pos
	for unicode.IsDigit(rune(l.current)) {
		l.advance()
	}
	return l.input[start:l.pos]
}

func (l *Lexer) NextToken() Token {
	l.skipWhitespace()
	
	if l.current == 0 {
		return Token{Type: EOF, Literal: ""}
	}
	
	var tok Token
	
	switch l.current {
	case '=':
		if l.peek() == '=' {
			l.advance()
			l.advance()
			tok = Token{Type: EQUAL_EQUAL, Literal: "=="}
		} else {
			tok = Token{Type: EQUALS, Literal: "="}
			l.advance()
		}
	case '+':
		tok = Token{Type: PLUS, Literal: "+"}
		l.advance()
	case '-':
		tok = Token{Type: MINUS, Literal: "-"}
		l.advance()
	case '>':
		tok = Token{Type: GREATER, Literal: ">"}
		l.advance()
	case '<':
		tok = Token{Type: LESS, Literal: "<"}
		l.advance()
	case '(':
		tok = Token{Type: LPAREN, Literal: "("}
		l.advance()
	case ')':
		tok = Token{Type: RPAREN, Literal: ")"}
		l.advance()
	case '{':
		tok = Token{Type: LBRACE, Literal: "{"}
		l.advance()
	case '}':
		tok = Token{Type: RBRACE, Literal: "}"}
		l.advance()
	case ';':
		tok = Token{Type: SEMICOLON, Literal: ";"}
		l.advance()
	case ',':
		tok = Token{Type: COMMA, Literal: ","}
		l.advance()
	default:
		if unicode.IsLetter(rune(l.current)) {
			literal := l.readIdentifier()
			tok = Token{Literal: literal}
			// Check keywords
			switch literal {
			case "int":
				tok.Type = INT
			case "if":
				tok.Type = IF
			case "return":
				tok.Type = RETURN
			default:
				tok.Type = IDENTIFIER
			}
		} else if unicode.IsDigit(rune(l.current)) {
			tok = Token{Type: NUMBER, Literal: l.readNumber()}
		} else {
			tok = Token{Type: ILLEGAL, Literal: string(l.current)}
			l.advance()
		}
	}
	
	return tok
}
