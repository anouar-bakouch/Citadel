int authenticate(int input, int flag) {
    int secret = 1234;
    int temp = 999;
    
    // Comparison 1: sanity check (low priority)
    if (temp > 0) {
        // Comparison 2: security check (high priority)
        if (input == secret) {
            return 1;
        }
    }
    
    return 0;
}
