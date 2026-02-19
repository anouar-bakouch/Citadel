package main

import (
	"fmt"
	"io/ioutil"
	"llvm-security-parser/pkg/codegen"
	"llvm-security-parser/pkg/lexer"
	"llvm-security-parser/pkg/parser"
	"os"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <input.c> <output.ll>\n", os.Args[0])
		os.Exit(1)
	}

	inputFile := os.Args[1]
	outputFile := os.Args[2]

	// Read input file
	inputBytes, err := ioutil.ReadFile(inputFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading input file: %v\n", err)
		os.Exit(1)
	}

	input := string(inputBytes)

	// Parse
	lex := lexer.New(input)
	p := parser.New(lex)

	program, err := p.ParseProgram()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Parse error: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Parsed successfully!\n")
	fmt.Printf("Functions: %d\n", len(program.Functions))
	for _, fn := range program.Functions {
		fmt.Printf("  Function: %s(%d params)\n", fn.Name, len(fn.Params))
		fmt.Printf("  Statements in body: %d\n", len(fn.Body.Statements))
	}

	// Generate LLVM IR
	gen := codegen.New()
	ir, err := gen.Generate(program)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Code generation error: %v\n", err)
		os.Exit(1)
	}

	// Write output file
	err = ioutil.WriteFile(outputFile, []byte(ir), 0644)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error writing output file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Generated LLVM IR written to %s\n", outputFile)
}
