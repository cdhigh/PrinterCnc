#PIC16F628A��̻����ư����λ��

##����
    * ֱ��֧�ִ󲿷����������gerber�ļ���ʽ������Eagle��Sprint-layout�ȡ�
    * ����Ҫ���Ҳο���themrleon��Ŀ����PCBʱ����ֱ�����gerber��������Ҫ����ͼ��Ȼ���ٵ��롣
    * ֧�ֳ��õ�gerber��ͼ���
    * ��б�ߣ�Բ�����̵Ȼ�ͼ����ת���ɿ��ư��ܽ��ܵ����
    * ֧�ֽ�ʹ��һ�ֻ��ʾ��ܻ������ֳߴ��ֱ�ߡ�
    * ֧��gerber�ļ����и������꣬��λ��������ʵ���������������
    

##ʹ�÷���
###ʹ��Դ���ļ�
    ��ȷ��װPython��pyserial��Ϳ���ִ��CncController.py����������ƽ̨��

###ʹ��cxFreezeԤ�����ļ�
    ��ǰ���ṩwindowsִ���ļ�

##��������˵��
    * ���ڳ�ʱʱ��ָ����������ư�ֱ��PC�յ���֮���ʱ�䡣
    * XYZ����ٶ�ʵ����ָ���ǲ����������֮�����ʱʱ�䣬����ʱ��Խ������Խ�졣���ǲ�������������Ƶ�ʹ��ߵĻ��������Х������������п��ܻᶪ������塣
    * ��ΪPython���б���������ʾ�շ����ݣ�Ƶ������ʱЧ�ʱȽϵͣ��ر�����������ʱ��������趨����Ҫ������Ŀ��̫��Ļ����ᵼ�½���ˢ���ٶȱȽ���������Ӱ���ӡ����ٶȣ�������Ҫ���ԣ����򲻽������ô�ġ���Ҫ������Ŀ����

##�����ļ�˵��
    * ����ʹ��ini�����ļ��������ã����˽����ϵ��Զ��׼��Ĳ��������⣬�˽������������ڽ�������ʾ�Ĳ���
    * MinimumX, MinimumY��Ҫ��Ϊ���ĸ���������λΪ΢�ף�Ϊ��֧�ָ����������Ҫ������������һ������С�ڴ�ֵ�����꣬���������궼����һ���ʵ�����ֵ���Ա����е����궼���ڴ������趨ֵ��
    * ShiftX, ShiftY���������������ɸ�����λΪ΢�ף���Щ������������GERBER�ļ�������ͼ��������ԭ��̫Զ�����µ�̻��г̲����򲻷��㴦����������ṩ��������ֵ��Ϊƽ��ͼ��ʹ�ã�����X���궼����ShiftX������Y���궼����ShiftY��
    * ���ͬʱ������ShiftX/ShiftY��MinimumX/MinimumY������������ƽ������ͼ����Ȼ�����ʵ�����ȷ��ͼ����������MinimumX/MinimumYҪ���������ShiftX/ShiftY����Ϊһ���ʵ��ĸ�����Ȼ��MinimumX/MinimumY����Ϊ0.0������Խ�����ͼ���ƶ���ԭ�㡣���ǲ�������������MinimumX/MinimumY��ô����Ű������õ�������߿���һ�룬���⻭��ʱԽ�硣

##��ǰ֧�����л�֧�ֵ�Gerber���Ժ�Ҫ��
    *���������ޣ���ѡ��ʵ�ִ󲿷ֳ������ԣ�������һЩ�����û����������Ŀ���ò�����RS274X�淶����ʵ�󲿷ֵĵ�·���Ű涼��֧�֣�����̫�����ģ�
    * ÿ����ͼ��X...Y...Z..���뵥�����У�ÿ����ͼ�е�X/Y/Z������ʡ�ԣ�����ǰ׺��G�����D���
    * ���̲�֧����Բ�ڷ�����֧����Բ�ڲ����ס�
    * ��֧��ֱ�߲岹ģʽG01����֧��Բ���岹G02/G03��
    * ��֧�ֺڰ׷��࣬��֧����Ӱ��ɫ��
    * ��֧��G36/G37����ģʽ��
    * ��֧���������귽ʽ����֧�־������귽ʽ��
    * ��֧��aperture�ꡣ
    * ���߽�֧��ʵ�ߣ���֧�����ߺ͵㻮�ߡ�

##���ư�ģ����˵��
    * ����λ�������Դ�һ���ǳ��򵥵�ģ������������λ�����͵Ļ�ͼ�������ʵ�ʵ�̻�һ���Ĵ������ͼ����������ʵ���������̻�֮ǰ��������Ч�������Ч������������Ҫ�˷�ʱ��������������ư塣
    * ���Ҫʹ��ģ��������������ģ��������ť�������һ�����ڣ���Ҫ�رմ˴��ڣ�ֱ���л���������԰��������Ĳ���һ���Ĳ�����֮�����н�Ҫ���͵����ư�������ֱ��ת����ģ��������������ͨ�����ڷ��������ư壬ģ�������յ���ͼ��������������ϻ��ͼ�������ͼ���Ƚϸ��ӣ���Ƚ����������ĵȺ򣩣����ͼ���Ƚ�С���¿��������̫������Խ�磬����Ե���ģ���������ϵġ�X/Y����(mm)��ֵ��������ȫ���������Ȼ������������ͼ����ɡ�
    * ��Ϊ���ư����ܺ��������ޣ���λ��ʹ�ú�����ˮƽ�ߺʹ�ֱ���������Ҫ���κ�ͼ������������ģ����ʱ����Ϊ��ͼ����̫�࣬�����ٶȻ����������һ��ʱ��Ľ��桰δ��Ӧ�����ԵȺ򼴿ɣ�����ͼ���Ĵ�С�͸��ӳ̶ȣ���ͼʱ����ܴӼ��뵽��ʮ�롣
    * �ڲ���Ҫģ��������ʱ�����Լ򵥵Ľ�ģ��������رգ���������������ֱ��ͨ�����ڷ�������ʵ���ư塣

##Sprint-layoutע�����
    * Sprint-layoutʹ�����½���Ϊ����ԭ�㣬��ˣ����Ű���ɺ����ʵ�������·��Ŀ��Ⱥ͸߶ȣ���ͼ�ξ����������½ǣ����������gerber�ļ����ʺϵ�̻�ʹ�ã�ͼ���������趨��ԭ��̫Զ����