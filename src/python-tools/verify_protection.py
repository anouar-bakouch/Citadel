#!/usr/bin/env python3
"""
Verification Engine for Data-Flow Protection
Verifies that protection code survives compiler optimizations
"""
import sys
import subprocess
import re

class ProtectionVerifier:
    def __init__(self):
        self.results = {
            'original_size': 0,
            'protected_size': 0,
            'optimized_size': 0,
            'abort_calls_protected': 0,
            'abort_calls_optimized': 0,
            'duplicate_cmp_protected': 0,
            'duplicate_cmp_optimized': 0,
            'verification_passed': False
        }
    
    def count_lines(self, filename):
        """Count non-empty, non-comment lines"""
        with open(filename, 'r') as f:
            lines = f.readlines()
        return len([l for l in lines if l.strip() and not l.strip().startswith(';')])
    
    def count_pattern(self, filename, pattern):
        """Count occurrences of a pattern in file"""
        with open(filename, 'r') as f:
            content = f.read()
        return len(re.findall(pattern, content))
    
    def verify_abort_present(self, filename):
        """Check if @abort() calls are present"""
        count = self.count_pattern(filename, r'call void @abort')
        return count > 0, count
    
    def verify_duplicates_present(self, filename):
        """Check if duplicate comparisons are present"""
        count = self.count_pattern(filename, r'%dup_\d+')
        return count > 0, count
    
    def verify_verification_present(self, filename):
        """Check if verification logic is present"""
        count = self.count_pattern(filename, r'%verify_\d+')
        return count > 0, count
    
    def compile_with_optimization(self, input_ir, output_ir, opt_level='O2'):
        """Compile IR with optimization"""
        try:
            # Use opt-14 to apply optimization passes
            cmd = [
                'opt-14',
                f'-{opt_level}',
                '-S',
                input_ir,
                '-o', output_ir
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[!] Optimization failed: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"[!] Error running optimizer: {e}")
            return False
    
    def verify_protected_ir(self, protected_ir_file):
        """Verify the protected IR has all protections"""
        print("\n[*] Verifying protected IR...")
        
        # Check abort calls
        has_abort, abort_count = self.verify_abort_present(protected_ir_file)
        self.results['abort_calls_protected'] = abort_count
        
        if not has_abort:
            print("  [!] ERROR: No abort() calls found in protected IR")
            return False
        print(f"  [✓] Found {abort_count} abort() calls")
        
        # Check duplicates
        has_dups, dup_count = self.verify_duplicates_present(protected_ir_file)
        self.results['duplicate_cmp_protected'] = dup_count
        
        if not has_dups:
            print("  [!] ERROR: No duplicate comparisons found")
            return False
        print(f"  [✓] Found {dup_count} duplicate comparisons")
        
        # Check verification logic
        has_verify, verify_count = self.verify_verification_present(protected_ir_file)
        if not has_verify:
            print("  [!] ERROR: No verification checks found")
            return False
        print(f"  [✓] Found {verify_count} verification checks")
        
        # Size metrics
        size = self.count_lines(protected_ir_file)
        self.results['protected_size'] = size
        
        return True
    
    def verify_optimized_ir(self, original_ir, optimized_ir):
        """Verify protections survived optimization"""
        print("\n[*] Verifying optimized IR...")
        
        # Check abort calls survived
        has_abort, abort_count = self.verify_abort_present(optimized_ir)
        self.results['abort_calls_optimized'] = abort_count
        
        if not has_abort:
            print("  [!] CRITICAL: abort() calls were removed by optimization!")
            print("      This means the optimizer eliminated our protection code.")
            return False
        
        print(f"  [✓] Protection check survived: {abort_count} abort() calls remain")
        
        # Check duplicate comparisons
        has_dups, dup_count = self.verify_duplicates_present(optimized_ir)
        self.results['duplicate_cmp_optimized'] = dup_count
        
        if dup_count == 0:
            print("  [!] WARNING: Duplicate comparisons were removed")
            print("      (This might be expected with aggressive optimization)")
        else:
            print(f"  [✓] {dup_count} duplicate comparisons survived")
        
        # Size metrics
        size = self.count_lines(optimized_ir)
        self.results['optimized_size'] = size
        
        return True
    
    def print_summary(self, original_ir):
        """Print verification results"""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        orig_size = self.count_lines(original_ir)
        self.results['original_size'] = orig_size
        prot_size = self.results['protected_size']
        opt_size = self.results['optimized_size']
        
        print(f"\n[Code Size Analysis]")
        print(f"  Original IR:       {orig_size} lines")
        print(f"  Protected IR:      {prot_size} lines (+{((prot_size-orig_size)/orig_size*100):.1f}%)")
        print(f"  After -O2:         {opt_size} lines ({((opt_size-orig_size)/orig_size*100):+.1f}% vs original)")
        
        print(f"\n[Protection Survival]")
        print(f"  Abort calls:       {self.results['abort_calls_protected']} → {self.results['abort_calls_optimized']} ✓")
        print(f"  Duplicates:        {self.results['duplicate_cmp_protected']} → {self.results['duplicate_cmp_optimized']}")
        
        overhead = ((prot_size - orig_size) / orig_size * 100)
        reduction = ((opt_size - orig_size) / orig_size * 100)
        
        print(f"\n[Key Findings]")
        print(f"  Overhead introduced:       {overhead:.1f}%")
        print(f"  Remaining after -O2:       {reduction:.1f}%")
        print(f"  Optimization reduction:    {(overhead - reduction):.1f}%")
        
        if self.results['abort_calls_optimized'] > 0:
            print(f"\n[✓] VERIFICATION PASSED")
            print(f"    Protections survived -O2 optimization!")
            self.results['verification_passed'] = True
        else:
            print(f"\n[!] VERIFICATION FAILED")
            print(f"    Protections were removed by optimization")
    
    def run_verification(self, original_ir, protected_ir):
        """Run complete verification pipeline"""
        print("[*] Starting protection verification...")
        
        # Step 1: Verify protected IR
        if not self.verify_protected_ir(protected_ir):
            return False
        
        # Step 2: Compile with optimization
        optimized_ir = protected_ir.replace('.ll', '_opt.ll')
        print(f"\n[*] Compiling with -O2 optimization...")
        if not self.compile_with_optimization(protected_ir, optimized_ir, 'O2'):
            return False
        print(f"  [✓] Optimized IR saved to {optimized_ir}")
        
        # Step 3: Verify optimized IR
        if not self.verify_optimized_ir(original_ir, optimized_ir):
            return False
        
        # Step 4: Print summary
        self.print_summary(original_ir)
        
        return self.results['verification_passed']

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 verify_protection.py original.ll protected.ll")
        print("\nExample:")
        print("  python3 verify_protection.py tests/inputs/password.ll tests/outputs/password_protected.ll")
        sys.exit(1)
    
    original_ir = sys.argv[1]
    protected_ir = sys.argv[2]
    
    verifier = ProtectionVerifier()
    success = verifier.run_verification(original_ir, protected_ir)
    
    sys.exit(0 if success else 1)
