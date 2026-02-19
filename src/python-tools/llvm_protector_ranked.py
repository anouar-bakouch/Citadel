#!/usr/bin/env python3
import sys

class LLVMProtector:
    def __init__(self):
        self.register_counter = 1000
        self.block_counter = 100
        self.comparisons = []
        
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
    
    def build_block_map(self, lines):
        """Build a dictionary mapping block labels to their instructions"""
        blocks = {}
        current_label = None
        current_instructions = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and (stripped[0].isdigit() or 'safe_' in stripped or 'fault_' in stripped):
                if ':' in stripped:
                    if current_label:
                        blocks[current_label] = current_instructions
                    current_label = stripped.split(':')[0]
                    current_instructions = []
            elif current_label:
                current_instructions.append(line)
        
        if current_label:
            blocks[current_label] = current_instructions
            
        return blocks
    
    def find_return_value(self, label, blocks, visited=None):
        """Find what value is returned from this path (1, 0, or None)"""
        if visited is None:
            visited = set()
        
        if label in visited:
            return None
        visited.add(label)
        
        block_lines = blocks.get(label, [])
        
        for line in block_lines:
            # Check for direct return with constant
            if 'ret i32 1' in line:
                return 1
            if 'ret i32 0' in line:
                return 0
            
            # Check for stores to return variable
            if 'store i32 1' in line:
                return 1
            if 'store i32 0' in line:
                return 0
                
            # Follow branches
            if 'br label' in line:
                parts = line.split()
                for part in parts:
                    if part.startswith('%'):
                        next_label = part.lstrip('%').rstrip(',')
                        result = self.find_return_value(next_label, blocks, visited)
                        if result is not None:
                            return result
        
        return None
    
    def score_comparison(self, cmp_result, lines, line_idx):
        """Score based on whether branches lead to different return values"""
        score = 0
        blocks = self.build_block_map(lines)
        
        for i in range(line_idx + 1, min(line_idx + 5, len(lines))):
            if 'br i1' in lines[i] and cmp_result in lines[i]:
                parts = lines[i].split()
                true_label = parts[4].lstrip('%').rstrip(',')
                false_label = parts[6].lstrip('%').rstrip(',') if len(parts) > 6 else None
                
                true_ret = self.find_return_value(true_label, blocks)
                false_ret = self.find_return_value(false_label, blocks) if false_label else None
                
                # Critical: branches lead to DIFFERENT returns (decision gate)
                if true_ret is not None and false_ret is not None and true_ret != false_ret:
                    score = 100
                # Medium: at least one path returns
                elif true_ret is not None or false_ret is not None:
                    score = 30
                
                break
        
        return score
    
    def process_file(self, input_file, output_file, threshold=50):
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        comparisons_to_protect = []
        for i, line in enumerate(lines):
            icmp_info = self.parse_icmp(line)
            if icmp_info:
                score = self.score_comparison(icmp_info['result'], lines, i)
                icmp_info['score'] = score
                icmp_info['line_num'] = i
                self.comparisons.append(icmp_info)
                
                if score >= threshold:
                    comparisons_to_protect.append(icmp_info)
                    print(f"[+] Will protect {icmp_info['result']} (score: {score})")
                else:
                    print(f"[-] Skipping {icmp_info['result']} (score: {score}, below threshold {threshold})")
        
        output = []
        added_abort = False
        protected_indices = {cmp['line_num'] for cmp in comparisons_to_protect}
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if 'target triple' in line and not added_abort:
                output.append(line)
                output.append('\ndeclare void @abort() noreturn\n\n')
                added_abort = True
                i += 1
                continue
            
            if i in protected_indices:
                icmp_info = next(cmp for cmp in comparisons_to_protect if cmp['line_num'] == i)
                
                output.append(line)
                dup_reg = f"%dup_{self.register_counter}"
                self.register_counter += 1
                
                op1 = icmp_info['op1']
                op2 = icmp_info['op2']
                output.append(f"  {dup_reg} = icmp eq {icmp_info['type']} {op1}, {op2}\n")
                
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
        
        total = len(self.comparisons)
        protected = len(comparisons_to_protect)
        print(f"\n[✓] Summary:")
        print(f"    Total comparisons: {total}")
        print(f"    Protected: {protected}")
        print(f"    Skipped: {total - protected}")
        if total > protected:
            reduction = ((total - protected) / total * 100)
            print(f"    Overhead reduction: ~{reduction:.0f}%")
        print(f"\n[✓] Protected IR written to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 llvm_protector_ranked.py input.ll output.ll [threshold]")
        sys.exit(1)
    
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    protector = LLVMProtector()
    protector.process_file(sys.argv[1], sys.argv[2], threshold)
