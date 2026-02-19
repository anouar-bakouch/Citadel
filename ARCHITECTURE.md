"""
Mermaid Diagram - LLVM Data-Flow Duplication & Security Pass Architecture
"""

# Architecture Overview Diagram
graph TD
    A["📄 C Source Code<br/>(authentication.c)"] -->|Tokenization| B["🔤 Lexer<br/>(Go)"]
    B -->|Token Stream| C["🌳 Parser<br/>(Recursive Descent)"]
    C -->|AST| D["⚙️ Code Generator<br/>(Go)"]
    D -->|"LLVM IR<br/>(Unprotected)"| E["📋 Unprotected IR<br/>(password.ll)"]
    
    E -->|IR Analysis| F["🤖 Protection Engine<br/>(Python)"]
    
    F -->|Compare Strategy| F1["🔍 Identify Comparisons<br/>(Find icmp instructions)"]
    F1 -->|Data Flow Analysis| F2["🧮 Bayesian Ranking<br/>(Score criticality)"]
    F2 -->|Score >= Threshold?| F3{Critical<br/>Variable?}
    
    F3 -->|Yes: Score 100| F4["✂️ Duplicate Check<br/>(Create shadow copy)"]
    F3 -->|No: Score < 50| F5["⊘ Skip<br/>(Don't protect)"]
    
    F4 -->|Add Verification| F6["✓ Insert Verification<br/>(Compare results)"]
    F5 -->|Pass Through| F6
    
    F6 -->|Protected IR| G["📋 Protected IR<br/>(password_protected.ll)"]
    
    G -->|Apply -O2| H["⚡ LLVM Optimizer<br/>(opt-14)"]
    H -->|Optimized IR| I["📋 Optimized IR<br/>(password_protected_opt.ll)"]
    
    G -->|Verification| J["🔬 Verification Engine<br/>(Python)"]
    I -->|Verification| J
    
    J -->|Count abort calls| J1["📊 Analysis<br/>- Abort survival<br/>- Duplicate survival<br/>- Size metrics"]
    J1 -->|Check Results| J2{Protections<br/>Survived?}
    
    J2 -->|Yes ✓| J3["✅ VERIFICATION PASSED<br/>(Robust against -O2)"]
    J2 -->|No ✗| J4["❌ VERIFICATION FAILED<br/>(Protections removed)"]
    
    J3 -->|Final IR| K["🔒 Fault-Protected IR"]
    K -->|Compile| L["⚙️ Compiler<br/>(clang-14)"]
    L -->|Linking| M["🎯 Protected Executable<br/>(detection enabled)"]
    
    J3 -->|Metrics| N["📈 Results<br/>- 25% overhead<br/>- Verification passed<br/>- Production-ready"]
    
    style A fill:#e1f5ff
    style E fill:#fff3e0
    style G fill:#f3e5f5
    style I fill:#e8f5e9
    style J3 fill:#c8e6c9
    style J4 fill:#ffcdd2
    style M fill:#fff9c4
    style N fill:#f0f4c3
