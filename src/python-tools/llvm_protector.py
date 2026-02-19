#!/usr/bin/env python3
import sys

class LLVMProtector:
    def __init__(self):
        self.register_counter = 1000
        self.block_counter = 100
        
    def parse_icmp(self, line):
        if 'icmp' not in line:
            return None
        parts = line.split()
        if len(parts) < 7:
            return None
        return {
            'result': parts[0],
            'type': parts[4],
            'op1': parts[5].rstrip(','),
            'op2': parts[6],
            'full_line': line.strip()
        }
    
    def process_file(self, input_file, output_file):
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        output = []
        # Add abort declaration after the target triple
        added_abort = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Add abort declaration after target triple
            if 'target triple' in line and not added_abort:
                output.append(line)
                output.append('\ndeclare void @abort() noreturn\n\n')
                added_abort = True
                i += 1
                continue
            
            icmp_info = self.parse_icmp(line)
            
            if icmp_info:
                output.append(line)
                dup_reg = f"%dup_{self.register_counter}"
                self.register_counter += 1
                output.append(f"  {dup_reg} = icmp eq {icmp_info['type']} {icmp_info['op1']}, {icmp_info['op2']}\n")
                
                verify_reg = f"%verify_{self.register_counter}"
                self.register_counter += 1
                output.append(f"  {verify_reg} = icmp eq i1 {icmp_info['result']}, {dup_reg}\n")
                
                i += 1
                while i < len(lines):
                    if 'br i1' in lines[i] and icmp_info['result'] in lines[i]:
                        br_parts = lines[i].split()
                        true_label = br_parts[4].rstrip(',')
                        false_label = br_parts[6]
                        
                        safe_label = f"safe_{self.block_counter}"
                        fault_label = f"fault_{self.block_counter}"
                        self.block_counter += 1
                        
                        output.append(f"  br i1 {verify_reg}, label %{safe_label}, label %{fault_label}\n\n")
                        output.append(f"{safe_label}:\n")
                        output.append(f"  br i1 {icmp_info['result']}, label {true_label}, label {false_label}\n\n")
                        output.append(f"{fault_label}:\n")
                        output.append(f"  call void @abort()\n")
                        output.append(f"  unreachable\n\n")
                        
                        print(f"[+] Protected: {icmp_info['result']} -> {safe_label}/{fault_label}")
                        i += 1
                        break
                    else:
                        output.append(lines[i])
                        i += 1
            else:
                output.append(line)
                i += 1
        
        with open(output_file, 'w') as f:
            f.writelines(output)
        
        print(f"\n[✓] Protected IR written to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 llvm_protector.py input.ll output.ll")
        sys.exit(1)
    
    protector = LLVMProtector()
    protector.process_file(sys.argv[1], sys.argv[2])
