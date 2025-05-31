// Simple hash function (djb2 algorithm)
unsigned int hash_password(const char* str) {
    unsigned int hash = 5381;
    int c;
    
    while ((c = *str++))
     // hash * 33 + c
        hash = ((hash << 5) + hash) + c;
    
    return hash;
}