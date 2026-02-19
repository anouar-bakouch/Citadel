; ModuleID = 'tests/inputs/complex.c'
source_filename = "tests/inputs/complex.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

declare void @abort() noreturn


; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @authenticate(i32 noundef %0, i32 noundef %1) #0 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  store i32 %0, i32* %4, align 4
  store i32 %1, i32* %5, align 4
  store i32 1234, i32* %6, align 4
  store i32 999, i32* %7, align 4
  %8 = load i32, i32* %7, align 4
  %9 = icmp sgt i32 %8, 0
  br i1 %9, label %10, label %16

10:                                               ; preds = %2
  %11 = load i32, i32* %4, align 4
  %12 = load i32, i32* %6, align 4
  %13 = icmp eq i32 %11, %12
  %dup_1000 = icmp eq i32 %11, %12
  %verify_1001 = icmp eq i1 %13, %dup_1000
  br i1 %verify_1001, label %safe_100, label %fault_100

safe_100:
  br i1 %13, label %14, label %15

fault_100:
  call void @abort()
  unreachable


14:                                               ; preds = %10
  store i32 1, i32* %3, align 4
  br label %17

15:                                               ; preds = %10
  br label %16

16:                                               ; preds = %15, %2
  store i32 0, i32* %3, align 4
  br label %17

17:                                               ; preds = %16, %14
  %18 = load i32, i32* %3, align 4
  ret i32 %18
}

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 14.0.6"}
