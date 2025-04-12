// Benchmark was created by MQT Bench on 2022-08-30
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 0.1.0
// Qiskit version: {'qiskit-terra': '0.20.0', 'qiskit-aer': '0.10.4', 'qiskit-ignis': '0.7.0', 'qiskit-ibmq-provider': '0.19.0', 'qiskit-aqua': None, 'qiskit': '0.36.0', 'qiskit-nature': '0.3.1', 'qiskit-finance': '0.3.1', 'qiskit-optimization': '0.3.2', 'qiskit-machine-learning': '0.4.0'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[8];
creg meas[8];
h q[0];
h q[1];
h q[2];
rzz(2.9773387028136) q[0],q[2];
h q[3];
rzz(2.9773387028136) q[2],q[3];
rx(-7.59609409662433) q[2];
h q[4];
h q[5];
rzz(2.9773387028136) q[1],q[5];
rzz(2.9773387028136) q[4],q[5];
rx(-7.59609409662433) q[5];
h q[6];
rzz(2.9773387028136) q[0],q[6];
rx(-7.59609409662433) q[0];
rzz(4.45490056183402) q[0],q[2];
rzz(2.9773387028136) q[4],q[6];
rx(-7.59609409662433) q[4];
rx(-7.59609409662433) q[6];
rzz(4.45490056183402) q[0],q[6];
rx(7.78655881572407) q[0];
h q[7];
rzz(2.9773387028136) q[1],q[7];
rx(-7.59609409662433) q[1];
rzz(4.45490056183402) q[1],q[5];
rzz(2.9773387028136) q[3],q[7];
rx(-7.59609409662433) q[3];
rzz(4.45490056183402) q[2],q[3];
rx(7.78655881572407) q[2];
rzz(4.45490056183402) q[4],q[5];
rzz(4.45490056183402) q[4],q[6];
rx(7.78655881572407) q[4];
rx(7.78655881572407) q[5];
rx(7.78655881572407) q[6];
rx(-7.59609409662433) q[7];
rzz(4.45490056183402) q[1],q[7];
rx(7.78655881572407) q[1];
rzz(4.45490056183402) q[3],q[7];
rx(7.78655881572407) q[3];
rx(7.78655881572407) q[7];
barrier q[0],q[1],q[2],q[3],q[4],q[5],q[6],q[7];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];
measure q[4] -> meas[4];
measure q[5] -> meas[5];
measure q[6] -> meas[6];
measure q[7] -> meas[7];
