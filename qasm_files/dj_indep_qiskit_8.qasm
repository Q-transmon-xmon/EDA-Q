// Benchmark was created by MQT Bench on 2022-08-30
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.1.0
// Qiskit version: {'qiskit-terra': '0.20.0', 'qiskit-aer': '0.10.4', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.0', 'qiskit-aqua': None, 'qiskit': '0.36.0', 'qiskit-nature': '0.3.1', 'qiskit-finance': '0.3.1', 'qiskit-optimization': '0.3.2', 'qiskit-machine-learning': '0.4.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[8];
creg c[7];
h q[0];
h q[1];
u2(0,0) q[2];
h q[3];
u2(0,0) q[4];
h q[5];
h q[6];
u2(-pi,-pi) q[7];
cx q[0],q[7];
h q[0];
cx q[1],q[7];
h q[1];
cx q[2],q[7];
u2(-pi,-pi) q[2];
cx q[3],q[7];
h q[3];
cx q[4],q[7];
u2(-pi,-pi) q[4];
cx q[5],q[7];
h q[5];
cx q[6],q[7];
h q[6];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
