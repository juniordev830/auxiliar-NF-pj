#import <Foundation/Foundation.h>

// Standalone macOS/GNUstep experiment: precise monetary arithmetic.
static NSDecimalNumber *CalculateTotal(NSString *amountText, NSString *rateText) {
    NSDecimalNumber *amount = [NSDecimalNumber decimalNumberWithString:amountText];
    NSDecimalNumber *rate = [NSDecimalNumber decimalNumberWithString:rateText];
    if ([amount isEqualToNumber:[NSDecimalNumber notANumber]] ||
        [rate isEqualToNumber:[NSDecimalNumber notANumber]] ||
        [amount compare:[NSDecimalNumber zero]] == NSOrderedAscending ||
        [rate compare:[NSDecimalNumber zero]] == NSOrderedAscending ||
        [rate compare:[NSDecimalNumber one]] == NSOrderedDescending) {
        return nil;
    }
    NSDecimalNumberHandler *rounding =
        [NSDecimalNumberHandler decimalNumberHandlerWithRoundingMode:NSRoundPlain
            scale:2 raiseOnExactness:NO raiseOnOverflow:YES
            raiseOnUnderflow:YES raiseOnDivideByZero:YES];
    NSDecimalNumber *multiplier =
        [[NSDecimalNumber one] decimalNumberByAdding:rate];
    return [amount decimalNumberByMultiplyingBy:multiplier withBehavior:rounding];
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 3) {
            fprintf(stderr, "Usage: transaction-total AMOUNT TAX_RATE_0_TO_1\n");
            return 2;
        }
        NSDecimalNumber *total = CalculateTotal(
            [NSString stringWithUTF8String:argv[1]],
            [NSString stringWithUTF8String:argv[2]]);
        if (total == nil) {
            fprintf(stderr, "Invalid amount or tax rate\n");
            return 1;
        }
        printf("%s\n", [[total stringValue] UTF8String]);
        return 0;
    }
}
